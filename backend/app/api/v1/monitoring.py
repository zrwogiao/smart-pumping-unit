"""实时监测接口。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import monitoring_service
from app.tasks import scheduler as scheduler_mod
from app.schemas.monitoring import RealtimeDataOut
from app.schemas.common import ok

router = APIRouter(prefix="/monitoring", tags=["实时监测"])


@router.get("/latest/{device_id}")
def latest(device_id: int, db: Session = Depends(get_db)):
    rec = monitoring_service.latest_realtime(db, device_id)
    return ok(RealtimeDataOut.model_validate(rec).model_dump() if rec else None)


@router.get("/series/{device_id}")
def series(device_id: int, limit: int = Query(100, ge=1, le=1000),
           db: Session = Depends(get_db)):
    recs = monitoring_service.series_realtime(db, device_id, limit)
    return ok([RealtimeDataOut.model_validate(r).model_dump() for r in recs])


@router.post("/simulate/start")
def simulate_start():
    scheduler_mod.start_scheduler()
    return ok({"running": True}, "模拟采集已启动")


@router.post("/simulate/stop")
def simulate_stop():
    scheduler_mod.stop_scheduler()
    return ok({"running": False}, "模拟采集已停止")


@router.get("/simulate/status")
def simulate_status():
    return ok({"running": scheduler_mod.is_running()})
