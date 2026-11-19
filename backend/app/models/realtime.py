"""实时监测数据（时序）。"""
from datetime import datetime
from sqlalchemy import Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class RealtimeData(Base):
    __tablename__ = "realtime_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    max_load: Mapped[float] = mapped_column(Float, default=0.0)
    min_load: Mapped[float] = mapped_column(Float, default=0.0)
    displacement: Mapped[float] = mapped_column(Float, default=0.0)
    current: Mapped[float] = mapped_column(Float, default=0.0)
    voltage: Mapped[float] = mapped_column(Float, default=0.0)
    stroke_rate: Mapped[float] = mapped_column(Float, default=0.0)
    stroke_length: Mapped[float] = mapped_column(Float, default=0.0)
    power: Mapped[float] = mapped_column(Float, default=0.0)
