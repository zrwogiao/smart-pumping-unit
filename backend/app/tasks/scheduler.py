"""定时任务：周期驱动数据模拟、诊断、告警判定与 WebSocket 推送。"""
import json
import random
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import settings
from app.core.database import SessionLocal
from app.services import device_service, monitoring_service, alarm_service, diagnosis_service_db
from app.services.constants import CONDITION_KEYS
from app.ws.realtime import manager

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

# 演示工况轮转池：大部分正常，偶尔各类故障（便于大屏看到诊断与告警）
_CONDITION_POOL = ["normal"] * 5 + CONDITION_KEYS[1:]  # normal*5 + 5类故障
_running = False
_tick = 0


async def _generate_tick():
    """一个采集周期：为每台运行设备生成数据+诊断+告警并推送。"""
    global _tick
    if not _running:
        return
    _tick += 1
    devices = device_service.get_all_devices_for_scheduler()
    if not devices:
        return

    db = SessionLocal()
    try:
        for device in devices:
            # 每隔若干 tick 切换一次工况，模拟工况变化
            condition = _CONDITION_POOL[(_tick + device["id"]) % len(_CONDITION_POOL)]

            rt = monitoring_service.generate_and_store_realtime(db, device, condition)
            alarms = alarm_service.check_and_create_alarms(db, device, rt)

            # 周期性生成示功图并诊断（每 2 个 tick 一次，减轻负担）
            diag_info = None
            card = None
            if _tick % 2 == 0:
                card = monitoring_service.generate_and_store_dynamo(db, device["id"], condition)
                diag, _ = diagnosis_service_db.analyze_and_store(db, card, method="rule")
                ca = alarm_service.create_condition_alarm(db, device["id"], diag.condition_label, diag.confidence)
                if ca:
                    alarms.append(ca)
                diag_info = {"condition": diag.condition, "label": diag.condition_label,
                             "confidence": diag.confidence}

            payload = {
                "type": "realtime",
                "device_id": device["id"],
                "data": {
                    "max_load": rt.max_load, "min_load": rt.min_load,
                    "displacement": rt.displacement, "current": rt.current,
                    "voltage": rt.voltage, "stroke_rate": rt.stroke_rate,
                    "stroke_length": rt.stroke_length, "power": rt.power,
                    "timestamp": str(rt.timestamp),
                },
                "diagnosis": diag_info,
                "dynamo": ({"displacement": json.loads(card.displacement),
                            "load": json.loads(card.load)} if card else None),
                "alarms": [{"id": a.id, "type": a.alarm_type, "level": a.level,
                            "message": a.message} for a in alarms],
            }
            await manager.broadcast(payload, device_id=device["id"])  # 含大屏订阅者(-1)
    except Exception as e:
        logger.exception(f"采集任务异常: {e}")
    finally:
        db.close()


def start_scheduler():
    global _running, scheduler
    if not scheduler.running:
        scheduler.add_job(_generate_tick, "interval",
                          seconds=settings.SIMULATION_INTERVAL_SECONDS, id="generate_tick")
        scheduler.start()
    _running = True


def stop_scheduler():
    global _running
    _running = False


def is_running() -> bool:
    return _running
