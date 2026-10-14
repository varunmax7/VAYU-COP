from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.enums import AircraftStatus
from app.models.mixins import ProvenanceMixin


class Aircraft(Base, ProvenanceMixin):
    __tablename__ = "aircraft"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    tail_number: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    callsign: Mapped[str] = mapped_column(String(32))
    type_code: Mapped[str] = mapped_column(ForeignKey("aircraft_types.code"), index=True)
    base_id: Mapped[str] = mapped_column(ForeignKey("bases.id"), index=True)
    status: Mapped[AircraftStatus] = mapped_column(String(16), default=AircraftStatus.READY)
    fuel_pct: Mapped[float] = mapped_column(Float, default=100.0)
    airframe_hours: Mapped[float] = mapped_column(Float, default=0.0)
    hours_since_maint: Mapped[float] = mapped_column(Float, default=0.0)
    hours_to_next_maint: Mapped[float] = mapped_column(Float, default=100.0)
    store_config: Mapped[str | None] = mapped_column(String(32), nullable=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    heading_deg: Mapped[float] = mapped_column(Float, default=0.0)
    alt_ft: Mapped[float] = mapped_column(Float, default=0.0)
    speed_kts: Mapped[float] = mapped_column(Float, default=0.0)
    # No FK constraint: avoids a circular aircraft<->assignments dependency (SQLite can't
    # ALTER TABLE ADD CONSTRAINT, so a circular FK pair can't be created across two tables).
    current_assignment_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    p_unserviceable_24h: Mapped[float] = mapped_column(Float, default=0.05)
