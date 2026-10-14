from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.enums import MissionStatus, MissionType, Priority, StoreCategory


class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    code: Mapped[str] = mapped_column(String(64))
    type: Mapped[MissionType] = mapped_column(String(16))
    priority: Mapped[Priority] = mapped_column(String(16))
    area_geojson: Mapped[dict] = mapped_column(JSON)
    area_name: Mapped[str] = mapped_column(String(16))  # sector, e.g. S4
    earliest_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    latest_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    on_station_min: Mapped[int] = mapped_column(Integer)
    required_aircraft: Mapped[int] = mapped_column(Integer, default=1)
    required_store: Mapped[StoreCategory | None] = mapped_column(String(16), nullable=True)
    requester_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[MissionStatus] = mapped_column(String(16), default=MissionStatus.REQUESTED)
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("missions.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(256), nullable=True)
