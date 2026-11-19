"""报表导出工具：CSV / Excel。"""
import io
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.realtime import RealtimeData


def export_realtime(db: Session, device_id: int | None = None,
                    start: str | None = None, end: str | None = None,
                    fmt: str = "csv") -> bytes:
    stmt = select(RealtimeData)
    if device_id:
        stmt = stmt.where(RealtimeData.device_id == device_id)
    if start:
        stmt = stmt.where(RealtimeData.timestamp >= start)
    if end:
        stmt = stmt.where(RealtimeData.timestamp <= end)
    rows = db.execute(stmt).scalars().all()

    data = [{
        "id": r.id, "device_id": r.device_id, "timestamp": str(r.timestamp),
        "max_load": r.max_load, "min_load": r.min_load, "displacement": r.displacement,
        "current": r.current, "voltage": r.voltage, "stroke_rate": r.stroke_rate,
        "stroke_length": r.stroke_length, "power": r.power,
    } for r in rows]
    df = pd.DataFrame(data)

    buf = io.BytesIO()
    if fmt == "excel":
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="实时监测数据")
    else:
        buf.write(df.to_csv(index=False).encode("utf-8-sig"))
    return buf.getvalue()
