from datetime import datetime

from app.schemas.common import CamelModel, ProvenanceRead


class WeatherObsRead(ProvenanceRead):
    id: str
    base_id: str
    valid_ts: datetime
    ceiling_ft: float
    visibility_km: float
    wind_kt: float
    gust_kt: float
    crosswind_kt: float
    precip_mm: float
    thunderstorm: bool
    is_forecast: bool


class WeatherCellRead(CamelModel):
    id: str
    label: str
    center_lat: float
    center_lon: float
    radius_km: float
    severity: str
    motion_deg: float
    motion_kts: float
