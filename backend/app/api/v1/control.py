"""远程控制接口。"""
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import control_service
from app.schemas.control import ParamsUpdateRequest, ControlLogOut
from app.schemas.common import ok

router = APIRouter(prefix="/control", tags=["远程控制"])


def _operator_id(authorization: str | None) -> int | None:
    # 教学简化：无 token 时记为 None
    return None


@router.post("/{device_id}/start")
def start(device_id: int, authorization: str | None = Header(None),
          db: Session = Depends(get_db)):
    log = control_service.execute_command(db, device_id, "start", operator_id=_operator_id(authorization))
    return ok(ControlLogOut.model_validate(log).model_dump(), "启动指令已执行")


@router.post("/{device_id}/stop")
def stop(device_id: int, authorization: str | None = Header(None),
         db: Session = Depends(get_db)):
    log = control_service.execute_command(db, device_id, "stop", operator_id=_operator_id(authorization))
    return ok(ControlLogOut.model_validate(log).model_dump(), "停止指令已执行")


@router.put("/{device_id}/params")
def set_params(device_id: int, params: ParamsUpdateRequest,
               authorization: str | None = Header(None), db: Session = Depends(get_db)):
    log = control_service.execute_command(db, device_id, "set_params",
                                          params=params.model_dump(exclude_unset=True),
                                          operator_id=_operator_id(authorization))
    return ok(ControlLogOut.model_validate(log).model_dump(), "参数已更新")


@router.get("/{device_id}/logs")
def logs(device_id: int, limit: int = 50, db: Session = Depends(get_db)):
    recs = control_service.list_logs(db, device_id, limit)
    return ok([ControlLogOut.model_validate(r).model_dump() for r in recs])
