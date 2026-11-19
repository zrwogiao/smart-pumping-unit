"""接口集成测试（FastAPI TestClient）。"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_login():
    r = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert r.status_code == 200
    data = r.json()
    assert data["code"] == 0
    assert data["data"]["access_token"]


def test_login_wrong_password():
    r = client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrong"})
    assert r.status_code == 401


def test_devices():
    r = client.get("/api/v1/devices")
    assert r.status_code == 200
    assert len(r.json()["data"]) >= 1


def test_generate_and_diagnose():
    r = client.post("/api/v1/dynamo/generate", json={"device_id": 1, "condition": "gas_affected"})
    assert r.status_code == 200
    card = r.json()["data"]
    assert card["condition_hint"] == "gas_affected"

    r2 = client.post("/api/v1/diagnosis/analyze",
                     json={"device_id": 1, "method": "rule", "dynamo_id": card["id"]})
    assert r2.status_code == 200
    assert r2.json()["data"]["condition"] == "gas_affected"


def test_conditions():
    r = client.get("/api/v1/diagnosis/conditions")
    assert r.status_code == 200
    assert len(r.json()["data"]) == 6


def test_control():
    r = client.post("/api/v1/control/1/stop")
    assert r.status_code == 200
    assert r.json()["data"]["result"] == "success"


def test_alarm_list():
    r = client.get("/api/v1/alarms")
    assert r.status_code == 200
    assert isinstance(r.json()["data"], list)
