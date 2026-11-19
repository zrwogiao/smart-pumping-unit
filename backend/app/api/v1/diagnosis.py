"""诊断接口。"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import monitoring_service, diagnosis_service_db
from app.services.constants import CONDITIONS
from app.schemas.diagnosis import DiagnosisAnalyzeRequest, DiagnosisOut, ConditionInfo
from app.schemas.common import ok

router = APIRouter(prefix="/diagnosis", tags=["工况诊断"])


@router.post("/analyze")
def analyze(req: DiagnosisAnalyzeRequest, db: Session = Depends(get_db)):
    card = None
    if req.dynamo_id:
        card = monitoring_service.get_dynamo(db, req.dynamo_id)
    else:
        card = monitoring_service.latest_dynamo(db, req.device_id)
    if not card:
        raise HTTPException(status_code=404, detail="未找到示功图，请先生成")

    diag, full = diagnosis_service_db.analyze_and_store(db, card, method=req.method)
    if req.method == "all":
        return ok(full, "诊断完成")
    return ok(DiagnosisOut.model_validate(diag).model_dump(), "诊断完成")


@router.get("/results/{device_id}")
def results(device_id: int, limit: int = 50, db: Session = Depends(get_db)):
    recs = diagnosis_service_db.list_results(db, device_id, limit)
    return ok([DiagnosisOut.model_validate(r).model_dump() for r in recs])


@router.get("/conditions")
def conditions():
    items = [ConditionInfo(key=k, label=v["label"],
                           description=v["description"], color=v["color"])
             for k, v in CONDITIONS.items()]
    return ok([i.model_dump() for i in items])
