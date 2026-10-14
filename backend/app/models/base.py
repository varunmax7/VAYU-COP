from sqlalchemy import JSON, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.enums import BaseStatus


class AirBase(Base):
    """A base/airfield. Named AirBase — 'Base' is taken by the SQLAlchemy declarative base."""

    __tablename__ = "bases"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    status: Mapped[BaseStatus] = mapped_column(String(16), default=BaseStatus.OPEN)
    runways: Mapped[int] = mapped_column(Integer, default=1)
    runway_capacity_per_15min: Mapped[int] = mapped_column(Integer, default=4)
    parking_capacity: Mapped[int] = mapped_column(Integer, default=20)
    fuel_stock_kl: Mapped[float] = mapped_column(Float, default=500.0)
    # [{"from": iso-datetime, "to": iso-datetime, "reason": str}, ...]
    closures: Mapped[list] = mapped_column(JSON, default=list)
