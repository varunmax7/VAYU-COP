"""Orchestrates the fusion pipeline (§8.2): runs every adapter on its own schedule,
normalises + resolves + stamps provenance for each raw record, persists to the DB, and
publishes domain events (consumed by the WS layer as `cop.delta`, and later by the
Phase 10 alert engine).
"""

import asyncio
import logging
import random
import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.events import (
    AircraftStatusChanged,
    AirspaceStatusChanged,
    CopDeltaReady,
    CrewStatusChanged,
    DataStale,
    DomainEvent,
    MissionRequested,
    StoresUpdated,
    ThreatDetected,
    ThreatUpdated,
    WeatherUpdated,
    event_bus,
)
from app.models.aircraft import Aircraft
from app.models.airspace import Airspace
from app.models.base import AirBase
from app.models.crew import CrewMember
from app.models.mission import Mission
from app.models.stores import StoreInventory
from app.models.threat import ThreatZone
from app.models.weather import WeatherObs
from app.services.fusion import normaliser
from app.services.fusion.adapters import ALL_ADAPTER_CLASSES, SourceAdapter, SourceHealth
from app.services.fusion.adapters.met_feed import BASE_STATION_CODES
from app.services.fusion.crosswalk import crosswalk
from app.services.fusion.resolver import (
    find_mergeable_threat,
    merge_confidence,
    merge_position,
    should_overwrite,
)
from app.services.fusion.staleness import sweep_staleness
from app.services.fusion.types import (
    AircraftPositionRecord,
    AircraftStatusRecord,
    AirspaceWindowRecord,
    CrewStatusRecord,
    MissionRequestRecord,
    StoreDeltaRecord,
    ThreatDetectionRecord,
    WeatherObsRecord,
)
from app.services.fusion.weather_client import get_forecast

logger = logging.getLogger("vayu.fusion.engine")

_STATION_TO_BASE = {v: k for k, v in BASE_STATION_CODES.items()}
_LEVEL_RANK = {"LOW": 0, "MED": 1, "HIGH": 2}


def square_polygon(center_lat: float, center_lon: float, half_width_deg: float = 0.3) -> dict:
    lat0, lat1 = center_lat - half_width_deg, center_lat + half_width_deg
    lon0, lon1 = center_lon - half_width_deg, center_lon + half_width_deg
    ring = [[lon0, lat0], [lon1, lat0], [lon1, lat1], [lon0, lat1], [lon0, lat0]]
    return {"type": "Polygon", "coordinates": [ring]}


class FusionEngine:
    def __init__(self) -> None:
        self.adapters: dict[str, SourceAdapter] = {cls.name: cls() for cls in ALL_ADAPTER_CLASSES}
        self.rng = random.Random()
        self._tasks: list[asyncio.Task] = []
        self._running = False

    def source_health(self) -> dict[str, SourceHealth]:
        return {name: a.health for name, a in self.adapters.items()}

    def set_enabled(self, name: str, enabled: bool) -> bool:
        adapter = self.adapters.get(name)
        if adapter is None:
            return False
        adapter.health.enabled = enabled
        return True

    # -- lifecycle -----------------------------------------------------------------

    async def start(self) -> None:
        if self._running:
            return
        self._running = True

        db = SessionLocal()
        try:
            crosswalk.refresh(db)
            self._warm_start(db)
        finally:
            db.close()

        for adapter in self.adapters.values():
            self._tasks.append(asyncio.create_task(self._run_adapter(adapter)))
        self._tasks.append(asyncio.create_task(self._staleness_loop()))
        self._tasks.append(asyncio.create_task(self._weather_forecast_loop()))

    async def stop(self) -> None:
        self._running = False
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

    def _warm_start(self, db: Session) -> None:
        """The scenario's seed timestamps are anchored to the exercise's fictional
        `sim_start`, which can be weeks away from the real wall-clock time the engine
        actually starts at (there's no sim clock until Phase 9 — adapters tick on real
        time). Without this, the very first threat-intel tick would find every seeded
        zone's `last_seen` outside the merge window and try to re-insert a duplicate, and
        the first staleness sweep would flag every entity stale on server start. Re-stamp
        every freshness timestamp to "now" once, without touching any business data.
        """
        now = datetime.now(UTC)
        for model in (Aircraft, CrewMember, Airspace, WeatherObs):
            for entity in db.query(model).all():
                entity.source_ts = now
                entity.fused_ts = now
                entity.stale = False
        for zone in db.query(ThreatZone).all():
            zone.source_ts = now
            zone.fused_ts = now
            zone.first_seen = now
            zone.last_seen = now
            zone.stale = False
        db.commit()

    # -- per-adapter loop ------------------------------------------------------------

    async def _run_adapter(self, adapter: SourceAdapter) -> None:
        while self._running:
            try:
                if adapter.health.enabled:
                    events, deltas = await asyncio.to_thread(self._tick, adapter)
                    for event in events:
                        await event_bus.publish(event)
                    if deltas:
                        await event_bus.publish(
                            CopDeltaReady(deltas=tuple(deltas), source=adapter.name)
                        )
            except Exception:
                adapter.health.record_error()
                logger.exception(f"{adapter.name} tick failed")
            await asyncio.sleep(adapter.interval_s)

    def _tick(self, adapter: SourceAdapter) -> tuple[list[DomainEvent], list[dict]]:
        db = SessionLocal()
        events: list[DomainEvent] = []
        deltas: list[dict] = []
        try:
            now = datetime.now(UTC)
            raw_records = adapter.generate(db, self.rng, now)
            if raw_records:
                adapter.health.record_message(now, count=len(raw_records))
            for raw in raw_records:
                try:
                    result = self._apply(db, adapter.name, raw, now)
                    if result:
                        ev, delta = result
                        if ev:
                            events.append(ev)
                        if delta:
                            deltas.append(delta)
                except Exception:
                    adapter.health.record_error()
                    logger.exception(f"{adapter.name} failed to apply record: {raw}")
            db.commit()
        finally:
            db.close()
        return events, deltas

    # -- dispatch ----------------------------------------------------------------

    def _apply(
        self, db: Session, source_name: str, raw: dict, now: datetime
    ) -> tuple[DomainEvent | None, dict | None] | None:
        if source_name == "maint_mis":
            return self._apply_aircraft_status(db, normaliser.parse_maint_mis(raw), now)
        if source_name == "crew_roster":
            return self._apply_crew_status(db, normaliser.parse_crew_roster(raw), now)
        if source_name == "stores_inv":
            return self._apply_store_delta(db, normaliser.parse_stores_inv(raw))
        if source_name == "met_feed":
            record = normaliser.parse_metar(raw["metar"], reference_date=now.date())
            return self._apply_weather_obs(db, record, now)
        if source_name == "airspace_notam":
            record = normaliser.parse_notam(raw["notam"], reference_date=now.date())
            return self._apply_airspace_window(db, record, now)
        if source_name == "threat_intel_a":
            return self._apply_threat_detection(db, normaliser.parse_threat_intel_a(raw), now)
        if source_name == "threat_intel_b":
            return self._apply_threat_detection(db, normaliser.parse_threat_intel_b(raw), now)
        if source_name == "track_feed":
            return self._apply_position(db, normaliser.parse_track_feed(raw), now)
        if source_name == "tasking":
            return self._apply_mission_request(db, normaliser.parse_tasking(raw))
        return None

    # -- apply handlers ------------------------------------------------------------

    def _apply_aircraft_status(
        self, db: Session, record: AircraftStatusRecord, now: datetime
    ) -> tuple[DomainEvent | None, dict | None] | None:
        aircraft_id = crosswalk.aircraft_id_for_tail(record.tail_number)
        aircraft = db.get(Aircraft, aircraft_id) if aircraft_id else None
        if aircraft is None:
            return None
        if not should_overwrite(
            "status",
            current_source=aircraft.source,
            current_ts=aircraft.source_ts,
            candidate_source=record.source,
            candidate_ts=record.source_ts,
        ):
            return None

        old_status = aircraft.status
        aircraft.status = record.status
        if record.hours_since_maint is not None:
            aircraft.hours_since_maint = record.hours_since_maint
        if record.hours_to_next_maint is not None:
            aircraft.hours_to_next_maint = record.hours_to_next_maint
        aircraft.source = record.source
        aircraft.source_ts = record.source_ts
        aircraft.fused_ts = now
        aircraft.confidence = 1.0
        aircraft.stale = False

        event = None
        if old_status != aircraft.status:
            event = AircraftStatusChanged(
                aircraft_id=aircraft.id,
                old_status=old_status,
                new_status=aircraft.status,
                source=record.source,
            )
        delta = {"kind": "aircraft", "id": aircraft.id, "patch": {"status": aircraft.status}}
        return event, delta

    def _apply_position(
        self, db: Session, record: AircraftPositionRecord, now: datetime
    ) -> tuple[DomainEvent | None, dict | None] | None:
        aircraft_id = crosswalk.aircraft_id_for_icao24(record.icao24)
        aircraft = db.get(Aircraft, aircraft_id) if aircraft_id else None
        if aircraft is None:
            return None

        aircraft.lat = record.lat
        aircraft.lon = record.lon
        aircraft.heading_deg = record.heading_deg
        aircraft.alt_ft = record.alt_ft
        aircraft.speed_kts = record.speed_kts
        aircraft.fused_ts = now
        aircraft.stale = False
        return None, None  # position deltas ride the dedicated 1 Hz aircraft.position stream

    def _apply_crew_status(
        self, db: Session, record: CrewStatusRecord, now: datetime
    ) -> tuple[DomainEvent | None, dict | None] | None:
        crew_id = crosswalk.crew_id_for_service_number(record.service_number)
        crew = db.get(CrewMember, crew_id) if crew_id else None
        if crew is None:
            return None

        old_status = crew.status
        crew.status = record.status
        if record.duty_start is not None:
            crew.duty_start = record.duty_start
        if record.duty_hours_24h is not None:
            crew.duty_hours_24h = record.duty_hours_24h
        crew.source = record.source
        crew.source_ts = record.source_ts
        crew.fused_ts = now
        crew.stale = False

        event = None
        if old_status != crew.status:
            event = CrewStatusChanged(
                crew_id=crew.id, old_status=old_status, new_status=crew.status, source=record.source
            )
        delta = {"kind": "crew", "id": crew.id, "patch": {"status": crew.status}}
        return event, delta

    def _apply_store_delta(
        self, db: Session, record: StoreDeltaRecord
    ) -> tuple[DomainEvent | None, dict | None] | None:
        store = (
            db.query(StoreInventory)
            .filter_by(base_id=record.base_id, category=record.category)
            .first()
        )
        if store is None:
            return None
        store.available = record.available
        store.reserved = record.reserved
        event = StoresUpdated(base_id=store.base_id, category=store.category, source=record.source)
        delta = {
            "kind": "store",
            "id": store.id,
            "patch": {"available": store.available, "reserved": store.reserved},
        }
        return event, delta

    def _apply_weather_obs(
        self, db: Session, record: WeatherObsRecord, now: datetime
    ) -> tuple[DomainEvent | None, dict | None] | None:
        base_id = _STATION_TO_BASE.get(record.base_id, record.base_id)
        if db.get(AirBase, base_id) is None:
            return None

        obs = WeatherObs(
            id=f"WXOBS-{uuid.uuid4().hex[:10]}",
            base_id=base_id,
            valid_ts=record.valid_ts,
            ceiling_ft=record.ceiling_ft,
            visibility_km=record.visibility_km,
            wind_kt=record.wind_kt,
            gust_kt=record.gust_kt,
            crosswind_kt=0.0,
            precip_mm=record.precip_mm,
            thunderstorm=record.thunderstorm,
            is_forecast=record.is_forecast,
            source=record.source,
            source_ts=record.source_ts,
            fused_ts=now,
            confidence=1.0,
            stale=False,
        )
        db.add(obs)
        event = WeatherUpdated(base_id=base_id, source=record.source)
        delta = {"kind": "weather", "id": base_id, "patch": {"thunderstorm": obs.thunderstorm}}
        return event, delta

    def _apply_airspace_window(
        self, db: Session, record: AirspaceWindowRecord, now: datetime
    ) -> tuple[DomainEvent | None, dict | None] | None:
        airspace = db.get(Airspace, record.airspace_id)
        if airspace is None:
            return None

        old_status = airspace.status
        airspace.status = record.status
        airspace.active_from = record.active_from
        airspace.active_to = record.active_to
        airspace.source = record.source
        airspace.source_ts = record.source_ts
        airspace.fused_ts = now
        airspace.stale = False

        event = None
        if old_status != airspace.status:
            event = AirspaceStatusChanged(
                airspace_id=airspace.id,
                old_status=old_status,
                new_status=airspace.status,
                source=record.source,
            )
        delta = {"kind": "airspace", "id": airspace.id, "patch": {"status": airspace.status}}
        return event, delta

    def _apply_threat_detection(
        self, db: Session, record: ThreatDetectionRecord, now: datetime
    ) -> tuple[DomainEvent | None, dict | None] | None:
        zones = db.query(ThreatZone).all()
        match = find_mergeable_threat(list(zones), record.lat, record.lon, record.source_ts)

        if match:
            sources = sorted(set(match.sources) | {record.source})
            match.center_lat, match.center_lon = merge_position(
                [
                    (match.center_lat, match.center_lon, match.confidence),
                    (record.lat, record.lon, record.confidence),
                ]
            )
            match.confidence = merge_confidence([match.confidence, record.confidence])
            match.sources = sources
            match.last_seen = record.source_ts
            if _LEVEL_RANK.get(record.level, 0) > _LEVEL_RANK.get(match.level, 0):
                match.level = record.level
            match.source = record.source
            match.source_ts = record.source_ts
            match.fused_ts = now
            match.stale = False
            event = ThreatUpdated(threat_id=match.id, source=record.source)
            delta = {
                "kind": "threat",
                "id": match.id,
                "patch": {"confidence": match.confidence, "level": match.level},
            }
            return event, delta

        new_zone = ThreatZone(
            id=f"T-{uuid.uuid4().hex[:6].upper()}",
            label=record.label_hint,
            level=record.level,
            center_lat=record.lat,
            center_lon=record.lon,
            radius_km=40.0,
            mobile=True,
            first_seen=record.source_ts,
            last_seen=record.source_ts,
            sources=[record.source],
            source=record.source,
            source_ts=record.source_ts,
            fused_ts=now,
            confidence=record.confidence,
            stale=False,
        )
        db.add(new_zone)
        db.flush()
        event = ThreatDetected(threat_id=new_zone.id, source=record.source)
        delta = {
            "kind": "threat",
            "id": new_zone.id,
            "patch": {"level": new_zone.level, "confidence": new_zone.confidence},
        }
        return event, delta

    def _apply_mission_request(
        self, db: Session, record: MissionRequestRecord
    ) -> tuple[DomainEvent | None, dict | None] | None:
        mission = Mission(
            id=f"MISSION-{uuid.uuid4().hex[:8].upper()}",
            code=record.code,
            type=record.type,
            priority=record.priority,
            area_geojson=square_polygon(record.center_lat, record.center_lon),
            area_name=record.area_name,
            earliest_start=record.earliest_start,
            latest_start=record.latest_start,
            on_station_min=record.on_station_min,
            required_aircraft=record.required_aircraft,
            required_store=record.required_store,
        )
        db.add(mission)
        db.flush()
        event = MissionRequested(
            mission_id=mission.id, priority=mission.priority, source=record.source
        )
        delta = {"kind": "mission", "id": mission.id, "patch": {"status": mission.status}}
        return event, delta

    # -- background sweeps ---------------------------------------------------------

    async def _staleness_loop(self) -> None:
        while self._running:
            await asyncio.sleep(5.0)  # §8.2 step 5: 5 s sweep
            try:
                transitions = await asyncio.to_thread(self._run_staleness_sweep)
                for t in transitions:
                    await event_bus.publish(
                        DataStale(
                            entity_kind=t.entity_kind,
                            entity_id=t.entity_id,
                            field_name=t.field_name,
                            source="staleness_sweep",
                        )
                    )
            except Exception:
                logger.exception("staleness sweep failed")

    def _run_staleness_sweep(self):
        db = SessionLocal()
        try:
            transitions = sweep_staleness(db)
            db.commit()
            return transitions
        finally:
            db.close()

    async def _weather_forecast_loop(self) -> None:
        while self._running:
            try:
                await self._refresh_weather_forecasts()
            except Exception:
                logger.exception("weather forecast refresh failed")
            await asyncio.sleep(600.0)  # every 10 minutes

    async def _refresh_weather_forecasts(self) -> None:
        from app.core.config import get_settings

        settings = get_settings()
        db = SessionLocal()
        try:
            bases = db.query(AirBase).all()
            base_coords = [(b.id, b.lat, b.lon) for b in bases]
        finally:
            db.close()

        for base_id, lat, lon in base_coords:
            now = datetime.now(UTC)
            hours = await get_forecast(
                lat, lon, mode=settings.weather_mode, rng=self.rng, now=now, hours=24
            )
            db = SessionLocal()
            try:
                db.query(WeatherObs).filter_by(base_id=base_id, is_forecast=True).delete()
                for hour in hours:
                    db.add(
                        WeatherObs(
                            id=f"WXFC-{uuid.uuid4().hex[:10]}",
                            base_id=base_id,
                            valid_ts=hour.valid_ts,
                            ceiling_ft=hour.ceiling_ft,
                            visibility_km=hour.visibility_km,
                            wind_kt=hour.wind_kt,
                            gust_kt=hour.gust_kt,
                            crosswind_kt=0.0,
                            precip_mm=hour.precip_mm,
                            thunderstorm=hour.thunderstorm,
                            is_forecast=True,
                            source="met_feed"
                            if settings.weather_mode != "synthetic"
                            else "synthetic",
                            source_ts=now,
                            fused_ts=now,
                            confidence=0.8,
                            stale=False,
                        )
                    )
                db.commit()
            finally:
                db.close()


fusion_engine = FusionEngine()
