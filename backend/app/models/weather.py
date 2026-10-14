from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.mixins import ProvenanceMixin


class WeatherObs(Base, ProvenanceMixin):
    __tablename__ = "weather_obs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    base_id: Mapped[str] = mapped_column(ForeignKey("bases.id"), index=True)
    valid_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ceiling_ft: Mapped[int] = mapped_column(Float)
    visibility_km: Mapped[float] = mapped_column(Float)
    wind_kt: Mapped[float] = mapped_column(Float)
    gust_kt: Mapped[float] = mapped_column(Float, default=0.0)
    crosswind_kt: Mapped[float] = mapped_column(Float, default=0.0)
    precip_mm: Mapped[float] = mapped_column(Float, default=0.0)
    thunderstorm: Mapped[bool] = mapped_column(Boolean, default=False)
    is_forecast: Mapped[bool] = mapped_column(Boolean, default=False)


class WeatherCell(Base):
    __tablename__ = "weather_cells"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    label: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    center_lat: Mapped[float] = mapped_column(Float)
    center_lon: Mapped[float] = mapped_column(Float)
    radius_km: Mapped[float] = mapped_column(Float)
    severity: Mapped[str] = mapped_column(String(16), default="moderate")
    motion_deg: Mapped[float] = mapped_column(Float, default=0.0)
    motion_kts: Mapped[float] = mapped_column(Float, default=0.0)
