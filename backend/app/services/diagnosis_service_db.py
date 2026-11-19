"""诊断落库服务：调用诊断引擎并将结果保存到数据库。"""
import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.models.diagnosis import DiagnosisResult
from app.models.dynamo import DynamoCard
from app.services import diagnosis_service


def analyze_and_store(db: Session, card: DynamoCard, method: str = "rule",
                      full_result: dict | None = None):
    """诊断并落库，返回 (落库记录, 完整诊断结果)。

    full_result 可由调用方预先计算（如 all 模式需要完整对比时）。
    """
    if full_result is None:
        disp = json.loads(card.displacement)
        load = json.loads(card.load)
        full_result = diagnosis_service.diagnose(disp, load, method=method)

    # all 模式落库主结果（rule），并补上特征供展示
    if method == "all":
        res = dict(full_result["results"]["rule"])
        res["features"] = full_result.get("features", {})
    else:
        res = full_result

    diag = DiagnosisResult(
        dynamo_id=card.id,
        device_id=card.device_id,
        condition=res["condition"],
        condition_label=res["label"],
        confidence=res["confidence"],
        features_json=json.dumps(res.get("features", {}), ensure_ascii=False),
        method=res.get("method", method),
        suggestion=res.get("suggestion", ""),
        diagnosed_at=datetime.now(),
    )
    db.add(diag)
    db.commit()
    db.refresh(diag)
    return diag, full_result


def list_results(db: Session, device_id: int, limit: int = 50) -> list[DiagnosisResult]:
    return list(db.execute(
        select(DiagnosisResult).where(DiagnosisResult.device_id == device_id)
        .order_by(desc(DiagnosisResult.diagnosed_at)).limit(limit)
    ).scalars().all())
