"""设备模型。"""
from datetime import datetime
from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    device_name: Mapped[str] = mapped_column(String(100), nullable=False)
    well_location: Mapped[str] = mapped_column(String(100), default="")
    status: Mapped[str] = mapped_column(String(20), default="running")  # running/stopped/fault
    stroke_length: Mapped[float] = mapped_column(Float, default=3.0)
    stroke_rate: Mapped[float] = mapped_column(Float, default=6.0)
    pump_depth: Mapped[float] = mapped_column(Float, default=1200.0)
    max_load_limit: Mapped[float] = mapped_column(Float, default=90.0)
    current_limit: Mapped[float] = mapped_column(Float, default=45.0)
    last_heartbeat: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
