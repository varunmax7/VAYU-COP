from sqlalchemy import JSON, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class AircraftType(Base):
    """A fleet type (e.g. SU30). Reference data; code is both the natural key and primary key."""

    __tablename__ = "aircraft_types"

    code: Mapped[str] = mapped_column(String(16), primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    roles: Mapped[list] = mapped_column(JSON, default=list)  # list[MissionType]
    cruise_kts: Mapped[int] = mapped_column(Integer)
    range_km: Mapped[int] = mapped_column(Integer)
    endurance_h: Mapped[float] = mapped_column(Float)
    turnaround_min: Mapped[int] = mapped_column(Integer)
    crew_required: Mapped[dict] = mapped_column(JSON, default=dict)  # {CrewRole: int}
    compatible_stores: Mapped[list] = mapped_column(JSON, default=list)  # list[StoreCategory]
    # {"ceiling_ft": int, "visibility_km": float, "crosswind_kt": int}
    wx_minima: Mapped[dict] = mapped_column(JSON, default=dict)
