"""示功图模拟引擎测试。"""
import pytest
from app.services import simulator
from app.services.features import extract_features
from app.services.constants import CONDITION_KEYS


def test_generate_shapes():
    """六类工况均能生成 100 点的闭合示功图。"""
    for cond in CONDITION_KEYS:
        s, p = simulator.generate_dynamo(cond)
        assert len(s) == len(p) == 100, cond
        assert min(s) >= 0 and max(s) <= 1, cond
        assert min(p) > 0, cond


@pytest.mark.parametrize("condition,feature,op,threshold", [
    ("pump_leak", "span", "lt", 35),
    ("gas_affected", "bulge_height", "gt", 8),
    ("wax", "pbase", "gt", 60),
    ("rod_parted", "span", "lt", 12),
    ("insufficient_liquid", "notch_depth", "gt", 5),
])
def test_condition_signature(condition, feature, op, threshold):
    """各工况的关键几何特征符合预期。"""
    medians = []
    for _ in range(10):
        s, p = simulator.generate_dynamo(condition)
        medians.append(extract_features(s, p)[feature])
    med = sorted(medians)[len(medians) // 2]
    if op == "lt":
        assert med < threshold, f"{condition}.{feature}={med} 应 < {threshold}"
    else:
        assert med > threshold, f"{condition}.{feature}={med} 应 > {threshold}"


def test_realtime():
    device = {"stroke_length": 3.0, "stroke_rate": 6.0}
    rt = simulator.generate_realtime(device)
    for key in ("max_load", "min_load", "displacement", "current", "voltage", "stroke_rate", "stroke_length", "power"):
        assert key in rt
