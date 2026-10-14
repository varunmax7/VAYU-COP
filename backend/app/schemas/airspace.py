from datetime import datetime

from app.models.enums import AirspaceKind, AirspaceStatus
from app.schemas.common import CamelModel, ProvenanceRead


class AirspaceRead(ProvenanceRead):
    id: str
    name: str
    kind: AirspaceKind
    polygon_geojson: dict
    floor_ft: int
    ceiling_ft: int
    active_from: datetime | None
    active_to: datetime | None
    status: AirspaceStatus


class AirspaceUpdate(CamelModel):
    status: AirspaceStatus | None = None
    active_from: datetime | None = None
    active_to: datetime | None = None
