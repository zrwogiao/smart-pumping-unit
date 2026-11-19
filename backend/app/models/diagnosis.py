"""诊断结果模型。"""
from datetime import datetime
from sqlalchemy import Integer, String, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class DiagnosisResult(Base):
    __tablename__ = "diagnosis_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dynamo_id: Mapped[int] = mapped_column(Integer, nullable=False)
    device_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    condition: Mapped[str] = mapped_column(String(30), nullable=False)
    condition_label: Mapped[str] = mapped_column(String(50), default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    features_json: Mapped[str] = mapped_column(Text, default="{}")
    method: Mapped[str] = mapped_column(String(20), default="rule")
    suggestion: Mapped[str] = mapped_column(Text, default="")
    diagnosed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
