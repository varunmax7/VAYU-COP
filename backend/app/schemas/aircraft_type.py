from app.schemas.common import CamelModel


class AircraftTypeRead(CamelModel):
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
