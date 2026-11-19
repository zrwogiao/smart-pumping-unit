"""远程控制相关 Schema。"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ParamsUpdateRequest(BaseModel):
    stroke_rate: float | None = None
    stroke_length: float | None = None
    max_load_limit: float | None = None
    current_limit: float | None = None


class ControlLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    command: str
    params_json: str
    operator_id: int | None
    result: str
    executed_at: datetime
