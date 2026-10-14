from datetime import datetime

from app.models.enums import MissionStatus, MissionType, Priority, StoreCategory
from app.schemas.common import CamelModel


class MissionRead(CamelModel):
    id: str
    code: str
    type: MissionType
    priority: Priority
    area_geojson: dict
    area_name: str
    earliest_start: datetime
    latest_start: datetime
    on_station_min: int
    required_aircraft: int
    required_store: StoreCategory | None
    requester_id: str | None
    status: MissionStatus
    parent_id: str | None
    notes: str | None


class MissionCreate(CamelModel):
    code: str
    type: MissionType
    priority: Priority
    area_geojson: dict
    area_name: str
    earliest_start: datetime
    latest_start: datetime
    on_station_min: int
    required_aircraft: int = 1
    required_store: StoreCategory | None = None
    requester_id: str | None = None
    notes: str | None = None


class MissionUpdate(CamelModel):
    priority: Priority | None = None
    earliest_start: datetime | None = None
    latest_start: datetime | None = None
    on_station_min: int | None = None
    required_aircraft: int | None = None
    required_store: StoreCategory | None = None
    status: MissionStatus | None = None
    notes: str | None = None
