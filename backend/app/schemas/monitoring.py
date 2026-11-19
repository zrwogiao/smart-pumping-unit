"""实时监测相关 Schema。"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class RealtimeDataOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    timestamp: datetime
    max_load: float
    min_load: float
    displacement: float
    current: float
    voltage: float
    stroke_rate: float
    stroke_length: float
    power: float


class SimulateRequest(BaseModel):
    device_id: int | None = None
    condition: str | None = None
