"""示功图模型。"""
from datetime import datetime
from sqlalchemy import Integer, String, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class DynamoCard(Base):
    __tablename__ = "dynamo_cards"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    source: Mapped[str] = mapped_column(String(20), default="simulated")
    condition_hint: Mapped[str] = mapped_column(String(30), default="normal")
    displacement: Mapped[str] = mapped_column(Text, nullable=False)  # JSON 数组
    load: Mapped[str] = mapped_column(Text, nullable=False)  # JSON 数组
    max_load: Mapped[float] = mapped_column(Float, default=0.0)
    min_load: Mapped[float] = mapped_column(Float, default=0.0)
    area: Mapped[float] = mapped_column(Float, default=0.0)
