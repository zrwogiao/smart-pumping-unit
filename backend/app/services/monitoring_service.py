"""监测与示功图服务：生成、落库、查询。"""
import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.models.realtime import RealtimeData
from app.models.dynamo import DynamoCard
from app.services.datasource import get_data_source
from app.services.features import extract_features
from app.services.constants import CONDITION_KEYS


def generate_and_store_realtime(db: Session, device: dict, condition: str = "normal") -> RealtimeData:
    data = get_data_source().read_realtime(device)
    rec = RealtimeData(device_id=device["id"], timestamp=datetime.now(), **data)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def latest_realtime(db: Session, device_id: int) -> RealtimeData | None:
    return db.execute(
        select(RealtimeData).where(RealtimeData.device_id == device_id)
        .order_by(desc(RealtimeData.timestamp)).limit(1)
    ).scalars().first()


def series_realtime(db: Session, device_id: int, limit: int = 100) -> list[RealtimeData]:
    return list(db.execute(
        select(RealtimeData).where(RealtimeData.device_id == device_id)
        .order_by(desc(RealtimeData.timestamp)).limit(limit)
    ).scalars().all()[::-1])


def generate_and_store_dynamo(db: Session, device_id: int, condition: str) -> DynamoCard:
    if condition not in CONDITION_KEYS:
        condition = "normal"
    disp, load = get_data_source().read_dynamo({"id": device_id}, condition)
    feats = extract_features(disp, load)
    card = DynamoCard(
        device_id=device_id,
        timestamp=datetime.now(),
        source="simulated",
        condition_hint=condition,
        displacement=json.dumps(disp),
        load=json.dumps(load),
        max_load=feats["pmax"],
        min_load=feats["pmin"],
        area=feats["area"],
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def latest_dynamo(db: Session, device_id: int) -> DynamoCard | None:
    return db.execute(
        select(DynamoCard).where(DynamoCard.device_id == device_id)
        .order_by(desc(DynamoCard.timestamp)).limit(1)
    ).scalars().first()


def get_dynamo(db: Session, dynamo_id: int) -> DynamoCard | None:
    return db.get(DynamoCard, dynamo_id)
