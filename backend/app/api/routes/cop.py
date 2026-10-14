from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.aircraft import Aircraft
from app.models.airspace import Airspace
from app.models.base import AirBase
from app.models.enums import PlanStatus
from app.models.mission import Mission
from app.models.plan import Assignment, Plan
from app.models.threat import ThreatZone
from app.models.weather import WeatherCell
from app.schemas.cop import CopSnapshotRead, RouteSegmentRead

router = APIRouter(prefix="/cop", tags=["cop"])


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


def _route_phase(assignment: Assignment, now: datetime) -> str:
    takeoff = _aware(assignment.takeoff_ts)
    land = _aware(assignment.land_ts)
    if now < takeoff:
        return "PLANNED"
    if now > land:
        return "FLOWN"
    return "AIRBORNE"


@router.get("/snapshot", response_model=CopSnapshotRead)
def get_snapshot(db: Session = Depends(get_db), _user=Depends(get_current_user)) -> CopSnapshotRead:
    bases = list(db.scalars(select(AirBase).order_by(AirBase.id)))
    aircraft = list(db.scalars(select(Aircraft).order_by(Aircraft.id)))
    airspace = list(db.scalars(select(Airspace).order_by(Airspace.id)))
    threats = list(db.scalars(select(ThreatZone).order_by(ThreatZone.id)))
    weather_cells = list(db.scalars(select(WeatherCell).order_by(WeatherCell.id)))

    active_plan = db.scalar(
        select(Plan).where(Plan.status == PlanStatus.APPROVED).order_by(Plan.version.desc())
    )
    routes: list[RouteSegmentRead] = []
    active_plan_summary = None
    if active_plan:
        now = datetime.now(UTC)
        stmt = select(Assignment).where(Assignment.plan_id == active_plan.id)
        assignments = list(db.scalars(stmt))
        mission_types = {
            m.id: m.type
            for m in db.scalars(
                select(Mission).where(Mission.id.in_([a.mission_id for a in assignments]))
            )
        }
        routes = [
            RouteSegmentRead(
                assignment_id=a.id,
                mission_id=a.mission_id,
                mission_type=mission_types.get(a.mission_id, "CAP"),
                aircraft_id=a.aircraft_id,
                phase=_route_phase(a, now),
                geometry=a.route_geojson,
            )
            for a in assignments
        ]
        active_plan_summary = {
            "id": active_plan.id,
            "version": active_plan.version,
            "profile": active_plan.profile,
            "kpis": active_plan.kpis,
            "confidence": active_plan.confidence,
        }

    return CopSnapshotRead(
        bases=bases,
        aircraft=aircraft,
        airspace=airspace,
        threats=threats,
        weather_cells=weather_cells,
        routes=routes,
        active_plan=active_plan_summary,
    )
