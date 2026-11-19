"""诊断相关 Schema。"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DiagnosisAnalyzeRequest(BaseModel):
    dynamo_id: int | None = None  # 不传则对最新一张示功图诊断
    device_id: int = 1
    method: str = "rule"  # rule/template/ml


class DiagnosisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dynamo_id: int
    device_id: int
    condition: str
    condition_label: str
    confidence: float
    features_json: str
    method: str
    suggestion: str
    diagnosed_at: datetime


class ConditionInfo(BaseModel):
    key: str
    label: str
    description: str
    color: str
