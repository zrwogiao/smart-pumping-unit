"""设备相关 Schema。"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DeviceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_code: str
    device_name: str
    well_location: str
    status: str
    stroke_length: float
    stroke_rate: float
    pump_depth: float
    max_load_limit: float
    current_limit: float
    last_heartbeat: datetime


class DeviceCreate(BaseModel):
    device_code: str
    device_name: str
    well_location: str = ""
    stroke_length: float = 3.0
    stroke_rate: float = 6.0
    pump_depth: float = 1200.0
    max_load_limit: float = 90.0
    current_limit: float = 45.0


class DeviceUpdate(BaseModel):
    device_name: str | None = None
    well_location: str | None = None
    status: str | None = None
    stroke_length: float | None = None
    stroke_rate: float | None = None
    pump_depth: float | None = None
    max_load_limit: float | None = None
    current_limit: float | None = None
