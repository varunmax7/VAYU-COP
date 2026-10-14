from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.enums import PlanProfile, PlanStatus


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[PlanStatus] = mapped_column(String(16), default=PlanStatus.DRAFT)
    profile: Mapped[PlanProfile] = mapped_column(String(16), default=PlanProfile.BALANCED)
    parent_plan_id: Mapped[str | None] = mapped_column(ForeignKey("plans.id"), nullable=True)
    trigger_event_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    objective: Mapped[float] = mapped_column(Float, default=0.0)
    # {coverage_pct, p1_p2_coverage_pct, avg_time_to_station_min, avg_risk,
    #  avg_fuel_margin_pct, utilisation_pct, aircraft_hours}
    kpis: Mapped[dict] = mapped_column(JSON, default=dict)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    solve_ms: Mapped[int] = mapped_column(Integer, default=0)
    solver_status: Mapped[str] = mapped_column(String(32), default="UNKNOWN")
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reject_reason: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    plan_id: Mapped[str] = mapped_column(ForeignKey("plans.id"), index=True)
    mission_id: Mapped[str] = mapped_column(ForeignKey("missions.id"), index=True)
    aircraft_id: Mapped[str] = mapped_column(ForeignKey("aircraft.id"), index=True)
    crew_ids: Mapped[list] = mapped_column(JSON, default=list)  # list[str]
    store_category: Mapped[str | None] = mapped_column(String(16), nullable=True)
    takeoff_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    on_station_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    off_station_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    land_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    route_geojson: Mapped[dict] = mapped_column(JSON)
    route_km: Mapped[float] = mapped_column(Float)
    time_to_station_min: Mapped[float] = mapped_column(Float)
    fuel_margin_pct: Mapped[float] = mapped_column(Float)
    risk_score: Mapped[float] = mapped_column(Float)
    reliability: Mapped[float] = mapped_column(Float, default=1.0)
    rationale: Mapped[list] = mapped_column(JSON, default=list)  # list[str]
    # [{"aircraft_id": str, "reason_code": str, "text": str}, ...]
    why_not: Mapped[list] = mapped_column(JSON, default=list)
    locked: Mapped[bool] = mapped_column(Boolean, default=False)


class UnassignedMission(Base):
    __tablename__ = "unassigned_missions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    plan_id: Mapped[str] = mapped_column(ForeignKey("plans.id"), index=True)
    mission_id: Mapped[str] = mapped_column(ForeignKey("missions.id"), index=True)
    reason_codes: Mapped[list] = mapped_column(JSON, default=list)  # list[ReasonCode]
    suggestion: Mapped[str | None] = mapped_column(String(256), nullable=True)
