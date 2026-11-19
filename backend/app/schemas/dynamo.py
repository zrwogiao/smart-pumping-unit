"""示功图相关 Schema。"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DynamoGenerateRequest(BaseModel):
    device_id: int = 1
    condition: str = "normal"  # normal/pump_leak/insufficient_liquid/gas_affected/wax/rod_parted


class DynamoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    timestamp: datetime
    source: str
    condition_hint: str
    displacement: str
    load: str
    max_load: float
    min_load: float
    area: float
