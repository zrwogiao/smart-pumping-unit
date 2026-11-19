"""历史数据与报表接口。"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.realtime import RealtimeData
from app.models.diagnosis import DiagnosisResult
from app.models.alarm import Alarm
from app.utils.exporter import export_realtime
from app.schemas.common import ok

router = APIRouter(prefix="/history", tags=["历史与报表"])


@router.get("/query")
def query(device_id: int | None = None, start: str | None = None,
          end: str | None = None, limit: int = 200, db: Session = Depends(get_db)):
    stmt = select(RealtimeData)
    if device_id:
        stmt = stmt.where(RealtimeData.device_id == device_id)
    if start:
        stmt = stmt.where(RealtimeData.timestamp >= start)
    if end:
        stmt = stmt.where(RealtimeData.timestamp <= end)
    stmt = stmt.order_by(RealtimeData.timestamp.desc()).limit(limit)
    rows = db.execute(stmt).scalars().all()
    data = [{"id": r.id, "device_id": r.device_id, "timestamp": str(r.timestamp),
             "max_load": r.max_load, "min_load": r.min_load, "current": r.current,
             "power": r.power, "stroke_rate": r.stroke_rate} for r in rows]
    return ok(data)


@router.get("/trend")
def trend(device_id: int = 1, metric: str = "max_load", limit: int = 100,
          db: Session = Depends(get_db)):
    allowed = {"max_load": RealtimeData.max_load, "current": RealtimeData.current,
               "power": RealtimeData.power, "min_load": RealtimeData.min_load}
    col = allowed.get(metric, RealtimeData.max_load)
    rows = db.execute(
        select(RealtimeData.timestamp, col).where(RealtimeData.device_id == device_id)
        .order_by(RealtimeData.timestamp.desc()).limit(limit)
    ).all()
    data = [{"timestamp": str(r[0]), "value": float(r[1])} for r in rows][::-1]
    return ok({"metric": metric, "points": data})


@router.get("/reports/summary")
def summary(db: Session = Depends(get_db)):
    total_records = db.execute(select(func.count(RealtimeData.id))).scalar() or 0
    avg_load = db.execute(select(func.avg(RealtimeData.max_load))).scalar() or 0
    avg_current = db.execute(select(func.avg(RealtimeData.current))).scalar() or 0
    alarm_count = db.execute(select(func.count(Alarm.id))).scalar() or 0

    # 工况分布
    dist_rows = db.execute(
        select(DiagnosisResult.condition_label, func.count(DiagnosisResult.id))
        .group_by(DiagnosisResult.condition_label)
    ).all()
    distribution = [{"label": r[0], "count": r[1]} for r in dist_rows]

    return ok({
        "total_records": total_records,
        "avg_load": round(float(avg_load), 2),
        "avg_current": round(float(avg_current), 2),
        "alarm_count": alarm_count,
        "condition_distribution": distribution,
    })


@router.get("/reports/export")
def export(device_id: int | None = None, start: str | None = None,
           end: str | None = None, format: str = "csv", db: Session = Depends(get_db)):
    content = export_realtime(db, device_id, start, end, format)
    if format == "excel":
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="realtime_report.xlsx"'},
        )
    return Response(
        content=content, media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="realtime_report.csv"'},
    )
