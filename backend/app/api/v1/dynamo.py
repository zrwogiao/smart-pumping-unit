"""示功图接口。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import monitoring_service
from app.services.constants import CONDITIONS
from app.schemas.dynamo import DynamoGenerateRequest, DynamoOut
from app.schemas.diagnosis import ConditionInfo
from app.schemas.common import ok

router = APIRouter(prefix="/dynamo", tags=["示功图"])


@router.post("/generate")
def generate(req: DynamoGenerateRequest, db: Session = Depends(get_db)):
    card = monitoring_service.generate_and_store_dynamo(db, req.device_id, req.condition)
    return ok(DynamoOut.model_validate(card).model_dump(), "生成成功")


@router.get("/latest/{device_id}")
def latest(device_id: int, db: Session = Depends(get_db)):
    card = monitoring_service.latest_dynamo(db, device_id)
    return ok(DynamoOut.model_validate(card).model_dump() if card else None)


@router.get("/{dynamo_id}")
def get_one(dynamo_id: int, db: Session = Depends(get_db)):
    card = monitoring_service.get_dynamo(db, dynamo_id)
    if not card:
        return ok(None, "示功图不存在")
    return ok(DynamoOut.model_validate(card).model_dump())


@router.get("/conditions/list")
def conditions():
    """工况字典。"""
    items = [ConditionInfo(key=k, label=v["label"],
                           description=v["description"], color=v["color"])
             for k, v in CONDITIONS.items()]
    return ok([i.model_dump() for i in items])
