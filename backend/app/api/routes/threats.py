import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.core.errors import api_error
from app.models.enums import UserRole
from app.models.threat import ThreatZone
from app.schemas.threat import ThreatZoneCreate, ThreatZoneRead, ThreatZoneUpdate

router = APIRouter(prefix="/threats", tags=["threats"])


@router.get("", response_model=list[ThreatZoneRead])
def list_threats(
    db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> list[ThreatZone]:
    return list(db.scalars(select(ThreatZone).order_by(ThreatZone.id)))


@router.post("", response_model=ThreatZoneRead, status_code=status.HTTP_201_CREATED)
def create_threat(
    payload: ThreatZoneCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(UserRole.INTEL)),
) -> ThreatZone:
    now = datetime.now(UTC)
    threat = ThreatZone(
        id=f"T-{uuid.uuid4().hex[:6].upper()}",
        first_seen=now,
        last_seen=now,
        source=payload.sources[0] if payload.sources else "threat_intel_a",
        source_ts=now,
        fused_ts=now,
        confidence=1.0,
        stale=False,
        **payload.model_dump(),
    )
    db.add(threat)
    db.commit()
    db.refresh(threat)
    return threat


@router.patch("/{threat_id}", response_model=ThreatZoneRead)
def update_threat(
    threat_id: str,
    payload: ThreatZoneUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(UserRole.INTEL)),
) -> ThreatZone:
    threat = db.get(ThreatZone, threat_id)
    if threat is None:
        raise api_error(404, f"Threat {threat_id} not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(threat, field, value)
    threat.last_seen = datetime.now(UTC)

    db.commit()
    db.refresh(threat)
    return threat
