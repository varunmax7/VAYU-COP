from app.schemas.aircraft import AircraftRead
from app.schemas.airspace import AirspaceRead
from app.schemas.base import AirBaseRead
from app.schemas.common import CamelModel
from app.schemas.threat import ThreatZoneRead
from app.schemas.weather import WeatherCellRead


class RouteSegmentRead(CamelModel):
    """Enough of an Assignment for the map's RouteLayer to style correctly
    (dashed/planned, solid/airborne, dotted/flown) without a second round trip."""

    assignment_id: str
    mission_id: str
    mission_type: str
    aircraft_id: str
    phase: str  # PLANNED | AIRBORNE | FLOWN
    geometry: dict


class CopSnapshotRead(CamelModel):
    bases: list[AirBaseRead]
    aircraft: list[AircraftRead]
    airspace: list[AirspaceRead]
    threats: list[ThreatZoneRead]
    weather_cells: list[WeatherCellRead]
    routes: list[RouteSegmentRead]
    active_plan: dict | None
