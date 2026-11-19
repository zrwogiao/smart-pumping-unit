"""数据库引擎、会话工厂、ORM 基类与初始化（建表 + 种子数据）。"""
import os
from datetime import datetime
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.core.config import settings

# SQLite 线程与外键支持
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    echo=False,
)

if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI 依赖注入：每个请求一个会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """建表并写入种子数据（幂等：已有数据则跳过）。"""
    os.makedirs("data", exist_ok=True)
    # 导入模型以确保元数据完整注册
    from app.models import (  # noqa: F401
        user, device, realtime, dynamo, diagnosis, alarm, control,
    )
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        _seed(db)
    finally:
        db.close()


def _seed(db: Session):
    from app.models.user import User
    from app.models.device import Device
    from app.core.security import hash_password

    # 管理员账号
    if db.query(User).count() == 0:
        admin = User(
            username="admin",
            password_hash=hash_password("admin123"),
            real_name="系统管理员",
            role="admin",
            is_active=True,
        )
        operator = User(
            username="operator",
            password_hash=hash_password("123456"),
            real_name="张三",
            role="operator",
            is_active=True,
        )
        db.add_all([admin, operator])

    # 演示设备
    if db.query(Device).count() == 0:
        devices = [
            Device(device_code="PUMP-001", device_name="1#抽油机", well_location="区块A-井001",
                   status="running", stroke_length=3.0, stroke_rate=6.0, pump_depth=1200.0,
                   max_load_limit=90.0, current_limit=45.0, last_heartbeat=datetime.now()),
            Device(device_code="PUMP-002", device_name="2#抽油机", well_location="区块A-井002",
                   status="running", stroke_length=2.7, stroke_rate=8.0, pump_depth=1500.0,
                   max_load_limit=85.0, current_limit=40.0, last_heartbeat=datetime.now()),
            Device(device_code="PUMP-003", device_name="3#抽油机", well_location="区块B-井003",
                   status="stopped", stroke_length=3.5, stroke_rate=5.0, pump_depth=1000.0,
                   max_load_limit=95.0, current_limit=50.0, last_heartbeat=datetime.now()),
            Device(device_code="PUMP-004", device_name="4#抽油机", well_location="区块B-井004",
                   status="running", stroke_length=2.5, stroke_rate=9.0, pump_depth=1800.0,
                   max_load_limit=80.0, current_limit=38.0, last_heartbeat=datetime.now()),
        ]
        db.add_all(devices)

    db.commit()
