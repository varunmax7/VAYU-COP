from app.models.enums import AircraftStatus
from app.schemas.common import CamelModel, ProvenanceRead


class AircraftRead(ProvenanceRead):
    id: str
    tail_number: str
    callsign: str
    type_code: str
    base_id: str
    status: AircraftStatus
    fuel_pct: float
    airframe_hours: float
    hours_since_maint: float
    hours_to_next_maint: float
    store_config: str | None
    lat: float
    lon: float
    heading_deg: float
    alt_ft: float
    speed_kts: float
    current_assignment_id: str | None
    p_unserviceable_24h: float


class AircraftStatusUpdate(CamelModel):
    status: AircraftStatus
    reason: str | None = None
