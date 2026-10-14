from datetime import datetime

from app.models.enums import ThreatLevel
from app.schemas.common import CamelModel, ProvenanceRead


class ThreatZoneRead(ProvenanceRead):
    id: str
    label: str
    level: ThreatLevel
    center_lat: float
    center_lon: float
    radius_km: float
    mobile: bool
    first_seen: datetime
    last_seen: datetime
    sources: list[str]


class ThreatZoneCreate(CamelModel):
    label: str
    level: ThreatLevel
    center_lat: float
    center_lon: float
    radius_km: float
    mobile: bool = False
    sources: list[str] = []


class ThreatZoneUpdate(CamelModel):
    level: ThreatLevel | None = None
    center_lat: float | None = None
    center_lon: float | None = None
    radius_km: float | None = None
