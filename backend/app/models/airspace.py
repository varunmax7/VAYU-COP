from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.enums import AirspaceKind, AirspaceStatus
from app.models.mixins import ProvenanceMixin


class Airspace(Base, ProvenanceMixin):
    __tablename__ = "airspaces"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    kind: Mapped[AirspaceKind] = mapped_column(String(16))
    polygon_geojson: Mapped[dict] = mapped_column(JSON)
    floor_ft: Mapped[int] = mapped_column(Integer, default=0)
    ceiling_ft: Mapped[int] = mapped_column(Integer, default=60000)
    active_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    active_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[AirspaceStatus] = mapped_column(String(16), default=AirspaceStatus.OPEN)
