"""远程控制日志模型。"""
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class ControlLog(Base):
    __tablename__ = "control_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    command: Mapped[str] = mapped_column(String(30), nullable=False)
    params_json: Mapped[str] = mapped_column(Text, default="")
    operator_id: Mapped[int] = mapped_column(Integer, nullable=True)
    result: Mapped[str] = mapped_column(String(20), default="success")
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
