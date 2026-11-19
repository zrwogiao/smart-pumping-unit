"""智能抽油机系统 FastAPI 应用入口。

- 注册 v1 API 路由（/api/v1）
- WebSocket 实时推送（/ws/monitoring/{device_id} 与 /ws/monitoring/all）
- 应用启动时初始化数据库；定时任务通过 /api/v1/monitoring/simulate/start 启动
- Swagger 文档：/docs  ReDoc：/redoc
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.router import api_router
from app.ws.realtime import manager
from app.tasks import scheduler as scheduler_mod


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler_mod.start_scheduler()  # 默认启动模拟采集，便于打开即见数据
    yield
    scheduler_mod.stop_scheduler()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="《智慧油气田应用开发》课程项目 —— 智能抽油机系统。支持实时监测、示功图诊断、历史报表与远程控制。",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION,
            "docs": "/docs", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.websocket("/ws/monitoring/{device_id}")
async def ws_monitoring(ws: WebSocket, device_id: int):
    """设备实时数据订阅。device_id=0 表示订阅全部设备（大屏用）。"""
    if device_id == 0:
        device_id = -1  # 用 -1 作为"全部"的键
    await manager.connect(ws, device_id)
    try:
        while True:
            await ws.receive_text()  # 保持连接，忽略客户端消息
    except WebSocketDisconnect:
        await manager.disconnect(ws, device_id)
