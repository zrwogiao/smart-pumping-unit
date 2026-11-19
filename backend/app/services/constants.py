"""工况字典常量：6 类典型抽油机工况的定义、几何特征描述与颜色。"""
from typing import Dict

# 工况 key -> {label, description, color, suggestion}
CONDITIONS: Dict[str, dict] = {
    "normal": {
        "label": "正常",
        "description": "示功图饱满、近似平行四边形，上下冲程载荷差稳定，无异常凸起或凹陷。",
        "color": "#67C23A",
        "suggestion": "抽油机运行正常，无需特殊处理，继续保持常规巡检。",
    },
    "pump_leak": {
        "label": "泵漏失",
        "description": "卸载线变缓、图形变瘦，示功图面积减小，上下冲程载荷差降低。",
        "color": "#E6A23C",
        "suggestion": "疑似泵阀漏失，建议检泵、检查游动阀与固定阀密封性。",
    },
    "insufficient_liquid": {
        "label": "供液不足",
        "description": "图形底部出现刀把状下凹，下冲程后半段载荷提前骤降并走平（充不满）。",
        "color": "#F56C6C",
        "suggestion": "地层供液不足，建议调小冲次或调小泵径，必要时采取增产措施。",
    },
    "gas_affected": {
        "label": "气体影响",
        "description": "图形右上角出现圆弧状凸起，上冲程末段受气体压缩影响。",
        "color": "#909399",
        "suggestion": "存在气体影响，建议安装气锚或优化泵挂深度，进行套管放气。",
    },
    "wax": {
        "label": "结蜡",
        "description": "上下冲程载荷整体抬高、曲线变宽、面积增大，伴随毛刺。",
        "color": "#409EFF",
        "suggestion": "井筒结蜡，建议热洗清蜡或加注防蜡剂，缩短清蜡周期。",
    },
    "rod_parted": {
        "label": "抽油杆断脱",
        "description": "载荷大幅下降，图形扁平贴近底部，上下冲程载荷差极小。",
        "color": "#C45656",
        "suggestion": "疑似抽油杆断脱，建议立即停机，起井检查抽油杆柱。",
    },
}

CONDITION_KEYS = list(CONDITIONS.keys())


def get_label(key: str) -> str:
    return CONDITIONS.get(key, {}).get("label", key)


def get_suggestion(key: str) -> str:
    return CONDITIONS.get(key, {}).get("suggestion", "")


def get_color(key: str) -> str:
    return CONDITIONS.get(key, {}).get("color", "#409EFF")
