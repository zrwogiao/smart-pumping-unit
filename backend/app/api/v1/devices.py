"""设备管理接口。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import device_service
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceOut
from app.schemas.common import ok

router = APIRouter(prefix="/devices", tags=["设备管理"])


@router.get("")
def list_devices(db: Session = Depends(get_db)):
    devices = device_service.list_devices(db)
    return ok([DeviceOut.model_validate(d).model_dump() for d in devices])


@router.post("")
def create_device(data: DeviceCreate, db: Session = Depends(get_db)):
    dev = device_service.create_device(db, data)
    return ok(DeviceOut.model_validate(dev).model_dump(), "创建成功")


@router.get("/{device_id}")
def get_device(device_id: int, db: Session = Depends(get_db)):
    dev = device_service.get_device(db, device_id)
    if not dev:
        raise HTTPException(status_code=404, detail="设备不存在")
    return ok(DeviceOut.model_validate(dev).model_dump())


@router.put("/{device_id}")
def update_device(device_id: int, data: DeviceUpdate, db: Session = Depends(get_db)):
    dev = device_service.update_device(db, device_id, data)
    if not dev:
        raise HTTPException(status_code=404, detail="设备不存在")
    return ok(DeviceOut.model_validate(dev).model_dump(), "更新成功")


@router.delete("/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    if not device_service.delete_device(db, device_id):
        raise HTTPException(status_code=404, detail="设备不存在")
    return ok(None, "删除成功")
