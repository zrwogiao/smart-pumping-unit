"""WebSocket 连接管理：按设备分组订阅，广播实时数据。"""
import asyncio
import json
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        # device_id -> set[WebSocket]
        self.by_device: Dict[int, Set[WebSocket]] = {}
        self.all_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket, device_id: int):
        await ws.accept()
        async with self._lock:
            self.by_device.setdefault(device_id, set()).add(ws)
            self.all_connections.add(ws)

    async def disconnect(self, ws: WebSocket, device_id: int):
        async with self._lock:
            if device_id in self.by_device:
                self.by_device[device_id].discard(ws)
                if not self.by_device[device_id]:
                    del self.by_device[device_id]
            self.all_connections.discard(ws)

    async def broadcast(self, message: dict, device_id: int):
        """广播给某设备的订阅者 + 大屏订阅者(device_id=-1)。"""
        targets = set(self.by_device.get(device_id, set())) | set(self.by_device.get(-1, set()))
        if not targets:
            return
        text = json.dumps(message, ensure_ascii=False, default=str)
        stale = []
        for ws in list(targets):
            try:
                await ws.send_text(text)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self.all_connections.discard(ws)
            for did in list(self.by_device.keys()):
                self.by_device[did].discard(ws)


manager = ConnectionManager()
