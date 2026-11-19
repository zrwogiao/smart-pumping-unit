"""数据模拟引擎：生成 6 类典型工况的示功图与实时监测数据。

物理基础：
- 位移按简谐运动：上冲程 s:0→1，下冲程 s:1→0（一个周期 100 点）
- 载荷以归一化区间 [0,1] 的分段曲线建模（0=最小载荷, 1=最大载荷），
  上/下冲程控制点的 x 均按递增排列以满足 np.interp 要求
- 实际载荷 = Pmin + p_norm * span
- 各工况通过不同的载荷曲线形状体现其几何特征（见 docs/04）
"""
import math
import random
import numpy as np
from typing import Tuple

from app.services.constants import CONDITION_KEYS

N_POINTS = 100
P_MIN = 25.0   # 参考最小载荷 kN
SPAN = 55.0    # 参考载荷跨度 kN（Pmax = P_MIN + SPAN = 80）


def _interp(s_arr: np.ndarray, points: list) -> np.ndarray:
    """按 (归一化位移 x 递增, 归一化载荷 y) 控制点线性插值。"""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    # 防御：确保 x 严格递增（去重）
    return np.interp(s_arr, xs, ys)


# 各工况的归一化载荷控制点（x 递增）
# up: 上冲程 s:0→1; down: 下冲程 s:1→0（但控制点按 x 递增书写）
_PROFILES = {
    "normal": {
        # 饱满平行四边形：上冲程高载荷、下冲程低载荷
        "up": [(0, 0.80), (0.15, 0.95), (0.85, 1.00), (1, 0.88)],
        "down": [(0, 0.12), (0.15, 0.05), (0.85, 0.05), (1, 0.12)],
        "noise": 1.0,
    },
    "pump_leak": {
        # 泵漏失：上下冲程载荷线靠拢，图形变瘦、面积减小
        "up": [(0, 0.62), (0.15, 0.72), (0.85, 0.74), (1, 0.64)],
        "down": [(0, 0.42), (0.15, 0.36), (0.85, 0.36), (1, 0.42)],
        "noise": 1.0,
    },
    "insufficient_liquid": {
        # 供液不足：下冲程接近下死点(s 小)时载荷骤降走平，形成底部刀把
        "up": [(0, 0.82), (0.15, 0.95), (0.85, 1.00), (1, 0.90)],
        "down": [(0, 0.02), (0.30, 0.02), (0.42, 0.28), (0.60, 0.34), (1, 0.12)],
        "noise": 1.0,
    },
    "gas_affected": {
        # 气体影响：上冲程末段(s→1)气体压缩形成圆弧凸起
        "up": [(0, 0.80), (0.15, 0.95), (0.70, 1.00), (0.86, 1.20), (1, 1.08)],
        "down": [(0, 0.12), (0.15, 0.05), (0.85, 0.05), (1, 0.12)],
        "noise": 1.0,
    },
    "wax": {
        # 结蜡：摩擦增大使上下冲程载荷整体抬高、图形变宽、毛刺多
        "up": [(0, 0.95), (0.15, 1.10), (0.85, 1.14), (1, 1.02)],
        "down": [(0, 0.38), (0.15, 0.30), (0.85, 0.30), (1, 0.38)],
        "noise": 2.2,
    },
    "rod_parted": {
        # 抽油杆断脱：载荷极低、图形扁平贴底、载荷差极小
        "up": [(0, 0.06), (0.5, 0.11), (1, 0.06)],
        "down": [(0, 0.02), (0.5, 0.06), (1, 0.02)],
        "noise": 1.0,
    },
}


def generate_dynamo(
    condition: str = "normal",
    max_load: float = 80.0,
    min_load: float = 25.0,
    noise: float | None = None,
) -> Tuple[list, list]:
    """生成一张示功图，返回 (归一化位移序列, 载荷序列(kN))。

    位移归一化到 [0,1]，实际位移 = 归一化值 * 冲程（前端换算）。
    """
    if condition not in CONDITION_KEYS:
        condition = "normal"

    prof = _PROFILES[condition]
    span = max_load - min_load
    base_noise = (noise if noise is not None else 0.8) * prof["noise"]

    # 一个周期：上冲程 s:0→1，下冲程 s:1→0
    t = np.linspace(0, 1, N_POINTS)
    s_up = 0.5 * (1 - np.cos(2 * np.pi * t[: N_POINTS // 2 + 1]))
    s_down = 0.5 * (1 - np.cos(2 * np.pi * t[N_POINTS // 2 :]))

    # 归一化载荷 → 实际载荷
    p_up_norm = _interp(s_up, prof["up"])
    p_down_norm = _interp(s_down, prof["down"])

    return _finish(s_up, s_down, p_up_norm, p_down_norm, min_load, span, base_noise)


def _finish(s_up, s_down, p_up_norm, p_down_norm, p_min, span, noise) -> Tuple[list, list]:
    """拼接上下冲程、加噪、平滑、映射载荷。"""
    p_up = p_min + p_up_norm * span
    p_down = p_min + p_down_norm * span

    # 下冲程去掉首点（与上冲程末点 s=1 重复）
    s = np.concatenate([s_up, s_down[1:]])
    p = np.concatenate([p_up, p_down[1:]])

    if noise > 0:
        p = p + np.random.normal(0, noise, size=p.shape)

    from scipy.signal import savgol_filter
    if len(p) >= 7:
        p = savgol_filter(p, 7, 2)

    return np.round(s, 4).tolist(), np.round(p, 3).tolist()


def generate_realtime(device: dict, condition: str = "normal") -> dict:
    """生成一条实时监测数据。"""
    S = device.get("stroke_length", 3.0)
    N = device.get("stroke_rate", 6.0)

    disp, load = generate_dynamo(condition)
    current = round(random.uniform(28, 42) * (1 + 0.1 * (N / 6 - 1)), 2)
    voltage = round(random.uniform(370, 390), 1)
    power = round(current * voltage * 1.732 * 0.85 / 1000, 2)

    return {
        "max_load": round(max(load), 2),
        "min_load": round(min(load), 2),
        "displacement": round(disp[len(disp) // 2] * S, 3),
        "current": current,
        "voltage": voltage,
        "stroke_rate": N,
        "stroke_length": S,
        "power": power,
    }
