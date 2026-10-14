from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.enums import StoreCategory


class StoreInventory(Base):
    __tablename__ = "store_inventory"

    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    base_id: Mapped[str] = mapped_column(ForeignKey("bases.id"), index=True)
    category: Mapped[StoreCategory] = mapped_column(String(16))
    available: Mapped[int] = mapped_column(Integer, default=0)
    reserved: Mapped[int] = mapped_column(Integer, default=0)
