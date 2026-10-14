"""Canonical, source-agnostic records that every adapter's raw output normalises into.
These are what the resolver (§8.2 steps 3-4) actually operates on."""

from datetime import datetime

from pydantic import BaseModel


class NormalizedRecord(BaseModel):
    source: str
    source_ts: datetime


class AircraftStatusRecord(NormalizedRecord):
    tail_number: str
    status: str
    hours_since_maint: float | None = None
    hours_to_next_maint: float | None = None
    snag: str | None = None


class AircraftPositionRecord(NormalizedRecord):
    icao24: str
    lat: float
    lon: float
    alt_ft: float
    heading_deg: float
    speed_kts: float


class CrewStatusRecord(NormalizedRecord):
    service_number: str
    status: str
    duty_start: datetime | None = None
    duty_hours_24h: float | None = None
    rest_ok: bool = True


class StoreDeltaRecord(NormalizedRecord):
    base_id: str
    category: str
    available: int
    reserved: int = 0


class WeatherObsRecord(NormalizedRecord):
    base_id: str
    valid_ts: datetime
    ceiling_ft: float
    visibility_km: float
    wind_kt: float
    gust_kt: float = 0.0
    precip_mm: float = 0.0
    thunderstorm: bool = False
    is_forecast: bool = False


class AirspaceWindowRecord(NormalizedRecord):
    airspace_id: str
    status: str
    active_from: datetime | None = None
    active_to: datetime | None = None


class ThreatDetectionRecord(NormalizedRecord):
    label_hint: str
    level: str
    lat: float
    lon: float
    confidence: float


class MissionRequestRecord(NormalizedRecord):
    code: str
    type: str
    priority: str
    area_name: str
    center_lat: float
    center_lon: float
    earliest_start: datetime
    latest_start: datetime
    on_station_min: int
    required_aircraft: int = 1
    required_store: str | None = None
