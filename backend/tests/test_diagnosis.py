"""诊断引擎准确率测试。"""
import pytest
from app.services import simulator
from app.services.features import extract_features
from app.services.diagnosis_service import diagnose_rule, diagnose_template, diagnose_ml
from app.services.constants import CONDITION_KEYS


@pytest.mark.parametrize("diagnose_fn,min_accuracy,samples", [
    (lambda s, p: diagnose_rule(extract_features(s, p)), 0.90, 20),
    (diagnose_template, 0.85, 10),
    (lambda s, p: diagnose_ml(extract_features(s, p)), 0.90, 20),
])
def test_diagnosis_accuracy(diagnose_fn, min_accuracy, samples):
    """各诊断方法对模拟数据的准确率达到阈值。"""
    correct = total = 0
    for cond in CONDITION_KEYS:
        for _ in range(samples):
            s, p = simulator.generate_dynamo(cond)
            result = diagnose_fn(s, p)
            if result["condition"] == cond:
                correct += 1
            total += 1
    accuracy = correct / total
    assert accuracy >= min_accuracy, f"准确率 {accuracy:.0%} < {min_accuracy:.0%}"


def test_diagnose_all():
    """all 模式返回三法对比结构。"""
    s, p = simulator.generate_dynamo("gas_affected")
    from app.services.diagnosis_service import diagnose
    res = diagnose(s, p, method="all")
    assert set(res["results"].keys()) == {"rule", "template", "ml"}
    assert "features" in res
