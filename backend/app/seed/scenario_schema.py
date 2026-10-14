"""Pydantic schema that seed/scenarios/vayu_shield.json must validate against (§7)."""

from pydantic import BaseModel, ConfigDict, Field


class ScenarioModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TheatreBounds(ScenarioModel):
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float


class ScenarioBase(ScenarioModel):
    id: str
    name: str
    code: str
    lat: float
    lon: float
    role: str
    runways: int = 1
    runway_capacity_per_15min: int = 4
    parking_capacity: int = 20
    fuel_stock_kl: float = 500.0


class ScenarioAllocation(ScenarioModel):
    base_id: str
    qty: int = Field(gt=0)


class ScenarioAircraftType(ScenarioModel):
    code: str
    name: str
    roles: list[str]
    cruise_kts: int
    range_km: int
    endurance_h: float
    turnaround_min: int
    crew_required: dict[str, int]
    compatible_stores: list[str]
    wx_minima: dict
    allocations: list[ScenarioAllocation]


class ScenarioAirspace(ScenarioModel):
    id: str
    name: str
    kind: str
    polygon_lat_lon: list[list[float]]  # [[lat, lon], ...] closed ring, >= 4 points
    floor_ft: int = 0
    ceiling_ft: int = 45000
    status: str = "OPEN"


class ScenarioThreat(ScenarioModel):
    id: str
    label: str
    level: str
    center_lat: float
    center_lon: float
    radius_km: float
    mobile: bool = False
    sources: list[str] = []


class ScenarioWeatherCell(ScenarioModel):
    id: str
    label: str
    center_lat: float
    center_lon: float
    radius_km: float
    severity: str = "moderate"
    motion_deg: float = 0.0
    motion_kts: float = 0.0


class ScenarioRelaySlots(ScenarioModel):
    count: int = Field(gt=1)
    aircraft_per_slot: int = Field(gt=0)
    slot_minutes: int = Field(gt=0)


class ScenarioMission(ScenarioModel):
    id: str
    code: str
    type: str
    priority: str
    area_name: str
    center_lat: float
    center_lon: float
    half_width_deg: float = 0.3
    earliest_start: str
    latest_start: str
    on_station_min: int
    required_aircraft: int = 1
    required_store: str | None = None
    notes: str | None = None
    relay_slots: ScenarioRelaySlots | None = None


class ScenarioDisruptionEvent(ScenarioModel):
    sim_time: str
    source: str
    type: str
    description: str
    payload: dict = {}


class Scenario(ScenarioModel):
    name: str
    seed: int
    sim_start: str
    theatre_bounds: TheatreBounds
    bases: list[ScenarioBase]
    aircraft_types: list[ScenarioAircraftType]
    airspaces: list[ScenarioAirspace]
    threats: list[ScenarioThreat]
    weather_cells: list[ScenarioWeatherCell]
    missions: list[ScenarioMission]
    disruption_timeline: list[ScenarioDisruptionEvent]
