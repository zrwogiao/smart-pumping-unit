"""历史与报表相关 Schema。"""
from pydantic import BaseModel


class HistoryQuery(BaseModel):
    device_id: int | None = None
    start: str | None = None
    end: str | None = None
    limit: int = 200


class TrendQuery(BaseModel):
    device_id: int = 1
    metric: str = "max_load"  # max_load/current/power
    start: str | None = None
    end: str | None = None
    limit: int = 100


class ExportRequest(BaseModel):
    device_id: int | None = None
    start: str | None = None
    end: str | None = None
    format: str = "csv"  # csv/excel
