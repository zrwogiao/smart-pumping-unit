"""告警相关 Schema。"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AlarmOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    alarm_type: str
    level: str
    message: str
    value: float | None
    status: str
    triggered_at: datetime
    acknowledged_by: int | None
    acknowledged_at: datetime | None
