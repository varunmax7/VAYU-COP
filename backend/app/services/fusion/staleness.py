"""Per-field max-age staleness (§8.2 step 5). The DB's ProvenanceMixin carries one
`fused_ts`/`stale` pair per *row*, not per field, so this sweep applies one max-age per
entity type — the category that matters most for that entity (position for a fast-moving
Aircraft row, status for slower-changing rows). Pure sync + no bus coupling, so it is
trivially unit-testable; the fusion engine is the one that turns transitions into events.
"""

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.aircraft import Aircraft
from app.models.airspace import Airspace
from app.models.crew import CrewMember
from app.models.threat import ThreatZone
from app.models.weather import WeatherObs
from app.services.fusion.time_utils import ensure_aware_utc

# Max age in seconds before a category's entities are considered stale (§8.2).
STALE_MAX_AGE_S = {
    "position": 10,  # Aircraft (lat/lon from track_feed)
    "status": 1800,  # CrewMember status, Airspace windows
    "weather": 3600,  # WeatherObs
    "threat": 1200,  # ThreatZone
}

_CATEGORY_BY_MODEL = {
    Aircraft: "position",
    CrewMember: "status",
    Airspace: "status",
    WeatherObs: "weather",
    ThreatZone: "threat",
}


@dataclass(frozen=True)
class StaleTransition:
    entity_kind: str
    entity_id: str
    field_name: str


def _sweep_model(db: Session, model, category: str, now: datetime) -> list[StaleTransition]:
    max_age = STALE_MAX_AGE_S[category]
    transitions: list[StaleTransition] = []
    for entity in db.query(model).all():
        age_s = (now - ensure_aware_utc(entity.fused_ts)).total_seconds()
        is_stale = age_s > max_age
        if is_stale and not entity.stale:
            transitions.append(StaleTransition(model.__name__, entity.id, category))
        entity.stale = is_stale
    return transitions


def sweep_staleness(db: Session, now: datetime | None = None) -> list[StaleTransition]:
    """Marks every tracked entity stale/fresh in place. Returns the rows that just
    transitioned from fresh to stale (fresh->fresh and already-stale rows are not returned).
    Caller is responsible for `db.commit()`.
    """
    now = now or datetime.now(UTC)
    transitions: list[StaleTransition] = []
    for model, category in _CATEGORY_BY_MODEL.items():
        transitions.extend(_sweep_model(db, model, category, now))
    return transitions
