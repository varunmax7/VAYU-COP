"""WebSocket connection manager and the periodic broadcast loops that drive the live
COP (§12.2): aircraft.position at 1 Hz, kpi.update at 1 Hz, fusion.health at 0.2 Hz, and
cop.delta forwarded from the fusion engine's event-bus notifications.
"""

import asyncio
import itertools
import logging
from datetime import UTC, datetime
from typing import Any

from fastapi import WebSocket
from sqlalchemy import select

from app.core.db import SessionLocal
from app.core.events import CopDeltaReady, event_bus
from app.models.aircraft import Aircraft
from app.services.fusion.engine import fusion_engine
from app.services.kpi_service import compute_kpis

logger = logging.getLogger("vayu.ws")


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._seq = itertools.count(1)

    def connect(self, websocket: WebSocket) -> None:
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    @property
    def connection_count(self) -> int:
        return len(self._connections)

    async def broadcast(self, msg_type: str, payload: Any) -> None:
        if not self._connections:
            return
        envelope = {
            "type": msg_type,
            "ts": datetime.now(UTC).isoformat(),
            "seq": next(self._seq),
            "payload": payload,
        }
        dead: list[WebSocket] = []
        for ws in self._connections:
            try:
                await ws.send_json(envelope)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


async def _aircraft_position_loop() -> None:
    while True:
        await asyncio.sleep(1.0)
        db = SessionLocal()
        try:
            rows = db.scalars(select(Aircraft)).all()
            batch = [
                {
                    "id": a.id,
                    "lat": a.lat,
                    "lon": a.lon,
                    "hdg": a.heading_deg,
                    "alt": a.alt_ft,
                    "spd": a.speed_kts,
                    "fuel": a.fuel_pct,
                }
                for a in rows
            ]
        finally:
            db.close()
        await manager.broadcast("aircraft.position", batch)


async def _kpi_loop() -> None:
    while True:
        await asyncio.sleep(1.0)
        db = SessionLocal()
        try:
            kpis = compute_kpis(db)
        finally:
            db.close()
        await manager.broadcast("kpi.update", kpis.model_dump(by_alias=True, mode="json"))


async def _fusion_health_loop() -> None:
    while True:
        await asyncio.sleep(5.0)  # 0.2 Hz
        health = {
            name: {
                "enabled": h.enabled,
                "status": h.status,
                "lastMsgTs": h.last_msg_ts.isoformat() if h.last_msg_ts else None,
                "msgsPerMin": h.msgs_per_min,
                "errors": h.errors,
                "lagS": None if h.lag_s == float("inf") else round(h.lag_s, 1),
            }
            for name, h in fusion_engine.source_health().items()
        }
        await manager.broadcast("fusion.health", health)


async def _cop_delta_forward_loop() -> None:
    queue = event_bus.subscribe(CopDeltaReady)
    try:
        while True:
            event = await queue.get()
            if isinstance(event, CopDeltaReady) and event.deltas:
                await manager.broadcast("cop.delta", list(event.deltas))
    finally:
        event_bus.unsubscribe(queue)


_background_tasks: list[asyncio.Task] = []


def start_broadcasters() -> None:
    _background_tasks.extend(
        [
            asyncio.create_task(_aircraft_position_loop()),
            asyncio.create_task(_kpi_loop()),
            asyncio.create_task(_fusion_health_loop()),
            asyncio.create_task(_cop_delta_forward_loop()),
        ]
    )


async def stop_broadcasters() -> None:
    for task in _background_tasks:
        task.cancel()
    await asyncio.gather(*_background_tasks, return_exceptions=True)
    _background_tasks.clear()
