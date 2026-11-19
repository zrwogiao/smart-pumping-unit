"""告警服务：判定、落库、确认、清除。"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.models.alarm import Alarm
from app.models.realtime import RealtimeData


def check_and_create_alarms(db: Session, device: dict, rt: RealtimeData) -> list[Alarm]:
    """基于实时数据判定告警，避免同类 active 告警重复创建。"""
    created = []
    rules = []

    if rt.max_load > device.get("max_load_limit", 90):
        rules.append(("overload", "critical", f"最大载荷超限: {rt.max_load:.1f}kN", rt.max_load))
    if rt.current > device.get("current_limit", 45):
        rules.append(("overcurrent", "warning", f"电机电流超限: {rt.current:.1f}A", rt.current))

    for alarm_type, level, message, value in rules:
        # 查是否已有未处理同类告警
        existing = db.execute(
            select(Alarm).where(Alarm.device_id == device["id"],
                                Alarm.alarm_type == alarm_type,
                                Alarm.status == "active")
        ).scalars().first()
        if not existing:
            alarm = Alarm(device_id=device["id"], alarm_type=alarm_type, level=level,
                          message=message, value=value, status="active",
                          triggered_at=datetime.now())
            db.add(alarm)
            created.append(alarm)
    if created:
        db.commit()
        for a in created:
            db.refresh(a)
    return created


def create_condition_alarm(db: Session, device_id: int, condition_label: str, confidence: float):
    """诊断出非正常工况时创建工况故障告警。"""
    if condition_label == "正常":
        return None
    existing = db.execute(
        select(Alarm).where(Alarm.device_id == device_id,
                            Alarm.alarm_type == "condition_fault",
                            Alarm.status == "active",
                            Alarm.message.like(f"%{condition_label}%"))
    ).scalars().first()
    if existing:
        return None
    alarm = Alarm(device_id=device_id, alarm_type="condition_fault", level="warning",
                  message=f"诊断异常工况: {condition_label}(置信度{confidence:.0%})",
                  status="active", triggered_at=datetime.now())
    db.add(alarm)
    db.commit()
    db.refresh(alarm)
    return alarm


def list_alarms(db: Session, status: str | None = None, level: str | None = None,
                limit: int = 100) -> list[Alarm]:
    stmt = select(Alarm)
    if status:
        stmt = stmt.where(Alarm.status == status)
    if level:
        stmt = stmt.where(Alarm.level == level)
    stmt = stmt.order_by(desc(Alarm.triggered_at)).limit(limit)
    return list(db.execute(stmt).scalars().all())


def acknowledge(db: Session, alarm_id: int, user_id: int) -> Alarm | None:
    alarm = db.get(Alarm, alarm_id)
    if not alarm:
        return None
    alarm.status = "acknowledged"
    alarm.acknowledged_by = user_id
    alarm.acknowledged_at = datetime.now()
    db.commit()
    db.refresh(alarm)
    return alarm


def clear(db: Session, alarm_id: int) -> Alarm | None:
    alarm = db.get(Alarm, alarm_id)
    if not alarm:
        return None
    alarm.status = "cleared"
    db.commit()
    db.refresh(alarm)
    return alarm
