"""示功图特征提取：从 (位移, 载荷) 序列计算诊断所需的特征参数。"""
import math
import numpy as np
from scipy.signal import savgol_filter
from typing import Dict


def polygon_area(x: np.ndarray, y: np.ndarray) -> float:
    """鞋带公式计算闭合曲线面积（带符号取绝对）。"""
    return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def extract_features(displacement: list, load: list) -> Dict[str, float]:
    """计算特征参数字典。"""
    s = np.array(displacement, dtype=float)
    p = np.array(load, dtype=float)
    if len(s) != len(p) or len(s) < 10:
        return _empty_features()

    # 平滑去噪（保留形状）
    if len(p) >= 7:
        p = savgol_filter(p, 7, 2)

    pmax = float(np.max(p))
    pmin = float(np.min(p))
    pavg = float(np.mean(p))
    span = pmax - pmin
    area = polygon_area(s, p)

    # 填充系数 η = A / (S * ΔP)，S 为归一化位移跨度（约 1）
    s_span = float(np.max(s) - np.min(s)) or 1.0
    fill = area / (s_span * span) if span > 0 else 0.0

    # 载荷基线（中心位置）：用于结蜡导致整体上移的判断
    pbase = (pmax + pmin) / 2

    # 上下冲程分离：前半段为上冲程（位移递增），后半段为下冲程
    half = len(s) // 2
    s_up, p_up = s[:half], p[:half]
    s_down, p_down = s[half:], p[half:]

    up_mean = float(np.mean(p_up))
    down_mean = float(np.mean(p_down))
    delta_p = up_mean - down_mean

    # 底部凹陷深度：下冲程中最小载荷与全局最小载荷基线偏离
    # 供液不足时下冲程出现深凹
    down_tail_min = float(np.min(p_down[int(len(p_down) * 0.5):]))
    notch_depth = float(np.median(p_down[:max(1, len(p_down)//4)]) - down_tail_min)
    notch_depth = max(0.0, notch_depth)

    # 右上凸起高度：上冲程末段相对上冲程中段的抬升
    up_head = float(np.max(p_up[int(len(p_up) * 0.7):]))
    up_mid = float(np.median(p_up[int(len(p_up) * 0.3):int(len(p_up) * 0.6)]))
    bulge_height = max(0.0, up_head - up_mid)

    return {
        "pmax": round(pmax, 3),
        "pmin": round(pmin, 3),
        "pavg": round(pavg, 3),
        "span": round(span, 3),
        "delta_p": round(delta_p, 3),
        "area": round(area, 3),
        "fill": round(fill, 4),
        "pbase": round(pbase, 3),
        "notch_depth": round(notch_depth, 3),
        "bulge_height": round(bulge_height, 3),
        "up_mean": round(up_mean, 3),
        "down_mean": round(down_mean, 3),
    }


def _empty_features() -> Dict[str, float]:
    keys = ["pmax", "pmin", "pavg", "span", "delta_p", "area", "fill",
            "pbase", "notch_depth", "bulge_height", "up_mean", "down_mean"]
    return {k: 0.0 for k in keys}
