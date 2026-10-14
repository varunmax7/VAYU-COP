from datetime import UTC, date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.aircraft import Aircraft
from app.models.alert import Alert
from app.models.crew import CrewMember
from app.models.enums import AircraftStatus, AlertSeverity, PlanStatus
from app.models.plan import Plan
from app.schemas.kpi import KpisRead


def _crew_is_current(crew: CrewMember, today: date) -> bool:
    if not crew.currency_expiry:
        return True
    return all(date.fromisoformat(expiry) >= today for expiry in crew.currency_expiry.values())


def _count(db: Session, model, *filters) -> int:
    stmt = select(func.count()).select_from(model)
    if filters:
        stmt = stmt.where(*filters)
    return db.scalar(stmt) or 0


def compute_kpis(db: Session) -> KpisRead:
    """Shared by GET /kpis and the `kpi.update` WebSocket broadcast loop."""
    aircraft_total = _count(db, Aircraft)
    aircraft_ready = _count(db, Aircraft, Aircraft.status == AircraftStatus.READY)
    active_sorties = _count(db, Aircraft, Aircraft.status == AircraftStatus.AIRBORNE)
    critical_alerts = _count(
        db, Alert, Alert.severity == AlertSeverity.CRITICAL, Alert.resolved.is_(False)
    )

    today = datetime.now(UTC).date()
    crew = list(db.scalars(select(CrewMember)))
    current_count = sum(1 for c in crew if _crew_is_current(c, today))
    crew_currency_pct = round(100 * current_count / len(crew), 1) if crew else 100.0

    active_plan = db.scalar(
        select(Plan).where(Plan.status == PlanStatus.APPROVED).order_by(Plan.version.desc())
    )
    ai_confidence_pct = round(active_plan.confidence * 100, 1) if active_plan else None

    return KpisRead(
        aircraft_ready=aircraft_ready,
        aircraft_total=aircraft_total,
        active_sorties=active_sorties,
        crew_currency_pct=crew_currency_pct,
        critical_alerts=critical_alerts,
        ai_confidence_pct=ai_confidence_pct,
        zulu_time=datetime.now(UTC),
    )
