"""告警模型。"""
from datetime import datetime
from sqlalchemy import Integer, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Alarm(Base):
    __tablename__ = "alarms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    alarm_type: Mapped[str] = mapped_column(String(30), nullable=False)
    level: Mapped[str] = mapped_column(String(10), default="warning")
    message: Mapped[str] = mapped_column(String(255), default="")
    value: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(15), default="active")  # active/acknowledged/cleared
    triggered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    acknowledged_by: Mapped[int] = mapped_column(Integer, nullable=True)
    acknowledged_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
