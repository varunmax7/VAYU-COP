"""Typed asyncio pub/sub event bus. Fusion publishes domain events here; the WebSocket
layer (and, from Phase 10 on, the alert engine) subscribes to react to them."""

import asyncio
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import ClassVar

logger = logging.getLogger("vayu.events")


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Base class for every event on the bus. Subclasses set `type` and add payload fields."""

    type: ClassVar[str] = "event"
    ts: datetime = field(default_factory=lambda: datetime.now(UTC))
    source: str = "system"


@dataclass(frozen=True, kw_only=True)
class AircraftStatusChanged(DomainEvent):
    type: ClassVar[str] = "AircraftStatusChanged"
    aircraft_id: str
    old_status: str
    new_status: str


@dataclass(frozen=True, kw_only=True)
class AircraftPositionUpdated(DomainEvent):
    type: ClassVar[str] = "AircraftPositionUpdated"
    aircraft_id: str


@dataclass(frozen=True, kw_only=True)
class CrewStatusChanged(DomainEvent):
    type: ClassVar[str] = "CrewStatusChanged"
    crew_id: str
    old_status: str
    new_status: str


@dataclass(frozen=True, kw_only=True)
class StoresUpdated(DomainEvent):
    type: ClassVar[str] = "StoresUpdated"
    base_id: str
    category: str


@dataclass(frozen=True, kw_only=True)
class ThreatDetected(DomainEvent):
    type: ClassVar[str] = "ThreatDetected"
    threat_id: str


@dataclass(frozen=True, kw_only=True)
class ThreatUpdated(DomainEvent):
    type: ClassVar[str] = "ThreatUpdated"
    threat_id: str


@dataclass(frozen=True, kw_only=True)
class AirspaceClosed(DomainEvent):
    type: ClassVar[str] = "AirspaceClosed"
    airspace_id: str


@dataclass(frozen=True, kw_only=True)
class AirspaceStatusChanged(DomainEvent):
    type: ClassVar[str] = "AirspaceStatusChanged"
    airspace_id: str
    old_status: str
    new_status: str


@dataclass(frozen=True, kw_only=True)
class WeatherUpdated(DomainEvent):
    type: ClassVar[str] = "WeatherUpdated"
    base_id: str


@dataclass(frozen=True, kw_only=True)
class MissionRequested(DomainEvent):
    type: ClassVar[str] = "MissionRequested"
    mission_id: str
    priority: str


@dataclass(frozen=True, kw_only=True)
class DataStale(DomainEvent):
    type: ClassVar[str] = "DataStale"
    entity_kind: str
    entity_id: str
    field_name: str


@dataclass(frozen=True, kw_only=True)
class CopDeltaReady(DomainEvent):
    """Carries the changed-entity patches from one fusion tick for the WS layer to forward
    as a `cop.delta` envelope (§8.2 step 7). Keeps the fusion engine decoupled from WS code."""

    type: ClassVar[str] = "CopDeltaReady"
    deltas: tuple[dict, ...] = ()


class EventBus:
    """In-process pub/sub. Each subscriber gets its own asyncio.Queue; publish() fans a
    DomainEvent out to every queue subscribed to its concrete type (or to "*" for all events).
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[DomainEvent]]] = {}

    def subscribe(self, *event_types: type[DomainEvent] | str) -> asyncio.Queue[DomainEvent]:
        queue: asyncio.Queue[DomainEvent] = asyncio.Queue()
        keys = [et if isinstance(et, str) else et.type for et in event_types] or ["*"]
        for key in keys:
            self._subscribers.setdefault(key, []).append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[DomainEvent]) -> None:
        for queues in self._subscribers.values():
            if queue in queues:
                queues.remove(queue)

    async def publish(self, event: DomainEvent) -> None:
        logger.debug(f"event published: {event.type} {event!r}")
        for key in (event.type, "*"):
            for queue in self._subscribers.get(key, []):
                await queue.put(event)

    async def stream(self, queue: asyncio.Queue[DomainEvent]) -> AsyncIterator[DomainEvent]:
        while True:
            yield await queue.get()


event_bus = EventBus()


def get_event_bus() -> EventBus:
    return event_bus
