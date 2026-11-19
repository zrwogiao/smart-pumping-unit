"""v1 路由汇总。"""
from fastapi import APIRouter
from app.api.v1 import auth, devices, monitoring, dynamo, diagnosis, history, control, alarm

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(devices.router)
api_router.include_router(monitoring.router)
api_router.include_router(dynamo.router)
api_router.include_router(diagnosis.router)
api_router.include_router(history.router)
api_router.include_router(control.router)
api_router.include_router(alarm.router)
