"""设备服务。"""
from sqlalchemy.orm import Session
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate
from app.core.database import SessionLocal
from sqlalchemy import select


def list_devices(db: Session) -> list[Device]:
    return list(db.execute(select(Device)).scalars().all())


def get_device(db: Session, device_id: int) -> Device | None:
    return db.get(Device, device_id)


def create_device(db: Session, data: DeviceCreate) -> Device:
    dev = Device(**data.model_dump())
    db.add(dev)
    db.commit()
    db.refresh(dev)
    return dev


def update_device(db: Session, device_id: int, data: DeviceUpdate) -> Device | None:
    dev = get_device(db, device_id)
    if not dev:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(dev, k, v)
    db.commit()
    db.refresh(dev)
    return dev


def delete_device(db: Session, device_id: int) -> bool:
    dev = get_device(db, device_id)
    if not dev:
        return False
    db.delete(dev)
    db.commit()
    return True


def get_all_devices_for_scheduler() -> list[dict]:
    """定时任务用独立会话读取所有运行中的设备。"""
    db = SessionLocal()
    try:
        devices = db.execute(select(Device).where(Device.status == "running")).scalars().all()
        return [{"id": d.id, "device_code": d.device_code, "stroke_length": d.stroke_length,
                 "stroke_rate": d.stroke_rate, "max_load_limit": d.max_load_limit,
                 "current_limit": d.current_limit} for d in devices]
    finally:
        db.close()
