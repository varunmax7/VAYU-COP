from app.models.enums import StoreCategory
from app.schemas.common import CamelModel


class StoreInventoryRead(CamelModel):
    id: str
    base_id: str
    category: StoreCategory
    available: int
    reserved: int


class StoreInventoryUpdate(CamelModel):
    available: int | None = None
    reserved: int | None = None
