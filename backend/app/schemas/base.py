from app.models.enums import BaseStatus
from app.schemas.common import CamelModel


class AirBaseRead(CamelModel):
    id: str
    name: str
    code: str
    lat: float
    lon: float
    status: BaseStatus
    runways: int
    runway_capacity_per_15min: int
    parking_capacity: int
    fuel_stock_kl: float
    closures: list[dict]  # [{"from": iso-datetime, "to": iso-datetime, "reason": str}, ...]


class AirBaseCreate(CamelModel):
    id: str
    name: str
    code: str
    lat: float
    lon: float
    status: BaseStatus = BaseStatus.OPEN
    runways: int = 1
    runway_capacity_per_15min: int = 4
    parking_capacity: int = 20
    fuel_stock_kl: float = 500.0
    closures: list[dict] = []


class AirBaseUpdate(CamelModel):
    status: BaseStatus | None = None
    runways: int | None = None
    runway_capacity_per_15min: int | None = None
    parking_capacity: int | None = None
    fuel_stock_kl: float | None = None
    closures: list[dict] | None = None
