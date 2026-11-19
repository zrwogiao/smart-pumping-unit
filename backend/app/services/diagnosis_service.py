"""工况诊断引擎：三层设计
1. 规则决策树（主，可解释）
2. 模板匹配（DTW/相关系数，对比兜底）
3. ML 分类器（进阶，KNN/决策树）

统一返回 {condition, label, confidence, method, features, suggestion, evidence}。
"""
import json
import numpy as np
from typing import Dict

from app.services.constants import CONDITIONS, get_label, get_suggestion
from app.services.features import extract_features
from app.services import simulator

# 参考基准（基于正常工况实测特征中位数：span≈53, pbase≈54）
REF = {
    "span": 53.0,
    "pbase": 54.0,
}


def diagnose_rule(features: Dict[str, float]) -> Dict:
    """第一层：可解释规则决策树。

    判定顺序体现优先级，各工况的关键区分特征（经实测校准）：
    - rod_parted: span 极小(<12)
    - pump_leak:  span 显著偏小(<35)
    - gas_affected: 右上凸起 bulge/span > 0.15
    - insufficient_liquid: 底部凹陷 notch/span > 0.13
    - wax: 载荷基线 pbase > 60
    - normal: 其余
    """
    span = features["span"]
    pbase = features["pbase"]
    notch = features["notch_depth"]
    bulge = features["bulge_height"]
    delta_p = features["delta_p"]

    def result(cond, conf, evidence):
        return {
            "condition": cond,
            "label": get_label(cond),
            "confidence": round(float(conf), 3),
            "method": "rule",
            "suggestion": get_suggestion(cond),
            "evidence": evidence,
        }

    # 1. 抽油杆断脱：载荷差极小，图形扁平贴底
    if span < 12:
        return result("rod_parted", 0.95,
                      f"载荷差极小(span={span:.1f}<12)，图形扁平贴底")

    # 2. 泵漏失：载荷差显著偏小，图形变瘦
    if span < 35:
        return result("pump_leak", 0.88,
                      f"载荷差显著降低(span={span:.1f}<35)，示功图变瘦")

    # 3. 气体影响：上冲程末段圆弧凸起（右上凸起相对跨度大）
    if span > 0 and bulge / span > 0.15:
        return result("gas_affected", 0.87,
                      f"上冲程末段圆弧凸起(bulge/span={bulge/span:.2f}>0.15)")

    # 4. 供液不足：下冲程底部刀把状凹陷
    if span > 0 and notch / span > 0.13:
        return result("insufficient_liquid", 0.86,
                      f"下冲程底部凹陷(notch/span={notch/span:.2f}>0.13)")

    # 5. 结蜡：载荷基线显著上移
    if pbase > 60:
        return result("wax", 0.85,
                      f"载荷基线上移(pbase={pbase:.1f}>60)，摩擦增大")

    # 6. 正常：各参数处于正常范围
    return result("normal", 0.9,
                  f"载荷差(span={span:.1f})、基线(pbase={pbase:.1f})均正常")


def _dtw_distance(a: np.ndarray, b: np.ndarray) -> float:
    """动态时间规整距离（简化 O(n*m) 实现）。"""
    n, m = len(a), len(b)
    dp = np.full((n + 1, m + 1), np.inf)
    dp[0, 0] = 0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = abs(a[i - 1] - b[j - 1])
            dp[i, j] = cost + min(dp[i - 1, j], dp[i, j - 1], dp[i - 1, j - 1])
    return dp[n, m]


def diagnose_template(displacement: list, load: list) -> Dict:
    """第二层：与标准工况模板做 DTW 相似度匹配。"""
    templates = {}
    for cond in CONDITIONS:
        s, p = simulator.generate_dynamo(cond, noise=0)  # 无噪声标准模板
        templates[cond] = np.array(p)

    target = np.array(load)
    # 归一化到相同量级后再比较
    def norm(x):
        x = np.array(x)
        rng = np.ptp(x) or 1
        return (x - np.min(x)) / rng

    target_n = norm(target)
    best_cond, best_dist = "normal", float("inf")
    dists = {}
    for cond, tmpl in templates.items():
        d = _dtw_distance(target_n, norm(tmpl))
        dists[cond] = d
        if d < best_dist:
            best_dist, best_cond = d, cond

    # 距离越小置信度越高（相对换算）
    sorted_d = sorted(dists.values())
    d0, d1 = sorted_d[0], sorted_d[1] if len(sorted_d) > 1 else sorted_d[0] * 2
    conf = 0.5 + 0.4 * (1 - d0 / d1) if d1 > 0 else 0.9

    return {
        "condition": best_cond,
        "label": get_label(best_cond),
        "confidence": round(float(max(0.5, min(0.95, conf))), 3),
        "method": "template",
        "suggestion": get_suggestion(best_cond),
        "evidence": f"DTW 距离最小: {best_cond}({best_dist:.3f})",
        "all_distances": {k: round(float(v), 3) for k, v in dists.items()},
    }


# 全局 ML 模型缓存
_ml_model = None
_ml_vectorizer_keys = list(CONDITIONS.keys())


def _train_ml_model():
    """用模拟引擎生成带标签样本训练 KNN 分类器（延迟训练，缓存复用）。"""
    from sklearn.neighbors import KNeighborsClassifier

    X, y = [], []
    samples_per_cond = 60
    for cond in _ml_vectorizer_keys:
        for _ in range(samples_per_cond):
            disp, load = simulator.generate_dynamo(cond)
            feats = extract_features(disp, load)
            X.append([feats["span"], feats["delta_p"], feats["area"],
                      feats["fill"], feats["pbase"], feats["notch_depth"],
                      feats["bulge_height"]])
            y.append(cond)
    model = KNeighborsClassifier(n_neighbors=5, weights="distance")
    model.fit(np.array(X), y)
    return model


def diagnose_ml(features: Dict[str, float]) -> Dict:
    """第三层：ML 分类器（KNN）。"""
    global _ml_model
    if _ml_model is None:
        _ml_model = _train_ml_model()
    x = np.array([[features["span"], features["delta_p"], features["area"],
                   features["fill"], features["pbase"], features["notch_depth"],
                   features["bulge_height"]]])
    proba = _ml_model.predict_proba(x)[0]
    classes = _ml_model.classes_
    idx = int(np.argmax(proba))
    cond = str(classes[idx])
    conf = float(proba[idx])
    return {
        "condition": cond,
        "label": get_label(cond),
        "confidence": round(conf, 3),
        "method": "ml",
        "suggestion": get_suggestion(cond),
        "evidence": f"KNN 概率最高: {cond}({conf:.2f})",
    }


def diagnose(displacement: list, load: list, method: str = "rule") -> Dict:
    """统一诊断入口。method: rule / template / ml / all。"""
    features = extract_features(displacement, load)
    if method == "template":
        res = diagnose_template(displacement, load)
        res["features"] = features
        return res
    if method == "ml":
        res = diagnose_ml(features)
        res["features"] = features
        return res
    if method == "all":
        results = {
            "rule": diagnose_rule(features),
            "template": diagnose_template(displacement, load),
            "ml": diagnose_ml(features),
        }
        return {"method": "all", "features": features, "results": results}

    res = diagnose_rule(features)
    res["features"] = features
    return res
