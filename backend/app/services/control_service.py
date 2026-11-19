"""远程控制服务。"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.models.control import ControlLog
from app.models.device import Device


def execute_command(db: Session, device_id: int, command: str,
                    params: dict | None = None, operator_id: int | None = None) -> ControlLog:
    dev = db.get(Device, device_id)
    result = "success"
    if dev:
        if command == "start":
            dev.status = "running"
        elif command == "stop":
            dev.status = "stopped"
        elif command == "set_params" and params:
            for k in ("stroke_rate", "stroke_length", "max_load_limit", "current_limit"):
                if k in params and params[k] is not None:
                    setattr(dev, k, params[k])
    else:
        result = "failed"

    log = ControlLog(device_id=device_id, command=command,
                     params_json=str(params or {}), operator_id=operator_id,
                     result=result, executed_at=datetime.now())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def list_logs(db: Session, device_id: int, limit: int = 50) -> list[ControlLog]:
    return list(db.execute(
        select(ControlLog).where(ControlLog.device_id == device_id)
        .order_by(desc(ControlLog.executed_at)).limit(limit)
    ).scalars().all())
