from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.enums import ThreatLevel
from app.models.mixins import ProvenanceMixin


class ThreatZone(Base, ProvenanceMixin):
    __tablename__ = "threat_zones"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    label: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    level: Mapped[ThreatLevel] = mapped_column(String(8))
    center_lat: Mapped[float] = mapped_column(Float)
    center_lon: Mapped[float] = mapped_column(Float)
    radius_km: Mapped[float] = mapped_column(Float)
    mobile: Mapped[bool] = mapped_column(Boolean, default=False)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sources: Mapped[list] = mapped_column(JSON, default=list)  # list[str]
