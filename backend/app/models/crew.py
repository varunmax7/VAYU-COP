from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.enums import CrewRole, CrewStatus
from app.models.mixins import ProvenanceMixin


class CrewMember(Base, ProvenanceMixin):
    __tablename__ = "crew_members"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    rank: Mapped[str] = mapped_column(String(16))
    role: Mapped[CrewRole] = mapped_column(String(32))
    base_id: Mapped[str] = mapped_column(ForeignKey("bases.id"), index=True)
    qualified_types: Mapped[list] = mapped_column(JSON, default=list)  # list[type_code]
    currency_expiry: Mapped[dict] = mapped_column(JSON, default=dict)  # {type_code: iso-date}
    status: Mapped[CrewStatus] = mapped_column(String(16), default=CrewStatus.AVAILABLE)
    duty_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duty_hours_24h: Mapped[float] = mapped_column(Float, default=0.0)
    duty_hours_7d: Mapped[float] = mapped_column(Float, default=0.0)
    last_rest_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fatigue_score: Mapped[float] = mapped_column(Float, default=10.0)
