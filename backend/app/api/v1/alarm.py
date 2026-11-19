"""告警接口。"""
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import alarm_service
from app.schemas.alarm import AlarmOut
from app.schemas.common import ok

router = APIRouter(prefix="/alarms", tags=["告警中心"])


@router.get("")
def list_alarms(status: str | None = None, level: str | None = None,
                limit: int = 100, db: Session = Depends(get_db)):
    recs = alarm_service.list_alarms(db, status, level, limit)
    return ok([AlarmOut.model_validate(r).model_dump() for r in recs])


@router.put("/{alarm_id}/ack")
def acknowledge(alarm_id: int, authorization: str | None = Header(None),
                db: Session = Depends(get_db)):
    alarm = alarm_service.acknowledge(db, alarm_id, 0)
    if not alarm:
        return ok(None, "告警不存在")
    return ok(AlarmOut.model_validate(alarm).model_dump(), "已确认")


@router.put("/{alarm_id}/clear")
def clear(alarm_id: int, db: Session = Depends(get_db)):
    alarm = alarm_service.clear(db, alarm_id)
    if not alarm:
        return ok(None, "告警不存在")
    return ok(AlarmOut.model_validate(alarm).model_dump(), "已清除")
