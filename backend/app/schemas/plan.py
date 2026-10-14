from datetime import datetime

from app.models.enums import PlanProfile, PlanStatus
from app.schemas.common import CamelModel


class AssignmentRead(CamelModel):
    id: str
    plan_id: str
    mission_id: str
    aircraft_id: str
    crew_ids: list[str]
    store_category: str | None
    takeoff_ts: datetime
    on_station_ts: datetime
    off_station_ts: datetime
    land_ts: datetime
    route_geojson: dict
    route_km: float
    time_to_station_min: float
    fuel_margin_pct: float
    risk_score: float
    reliability: float
    rationale: list[str]
    why_not: list[dict]
    locked: bool


class UnassignedMissionRead(CamelModel):
    id: str
    plan_id: str
    mission_id: str
    reason_codes: list[str]
    suggestion: str | None


class PlanRead(CamelModel):
    id: str
    version: int
    status: PlanStatus
    profile: PlanProfile
    parent_plan_id: str | None
    trigger_event_id: str | None
    objective: float
    kpis: dict
    confidence: float
    solve_ms: int
    solver_status: str
    created_by: str | None
    approved_by: str | None
    approved_at: datetime | None
    reject_reason: str | None
    created_at: datetime
    assignments: list[AssignmentRead] = []
    unassigned: list[UnassignedMissionRead] = []
