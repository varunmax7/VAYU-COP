from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.core.errors import api_error
from app.models.aircraft import Aircraft
from app.models.enums import AircraftStatus, UserRole
from app.schemas.aircraft import AircraftRead, AircraftStatusUpdate

router = APIRouter(prefix="/aircraft", tags=["aircraft"])


@router.get("", response_model=list[AircraftRead])
def list_aircraft(
    base: str | None = None,
    type: str | None = None,
    status: AircraftStatus | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[Aircraft]:
    stmt = select(Aircraft)
    if base:
        stmt = stmt.where(Aircraft.base_id == base)
    if type:
        stmt = stmt.where(Aircraft.type_code == type)
    if status:
        stmt = stmt.where(Aircraft.status == status)
    stmt = stmt.order_by(Aircraft.id).offset(offset).limit(limit)
    return list(db.scalars(stmt))


@router.get("/{aircraft_id}", response_model=AircraftRead)
def get_aircraft(
    aircraft_id: str, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> Aircraft:
    aircraft = db.get(Aircraft, aircraft_id)
    if aircraft is None:
        raise api_error(404, f"Aircraft {aircraft_id} not found")
    return aircraft


@router.patch("/{aircraft_id}/status", response_model=AircraftRead)
def update_aircraft_status(
    aircraft_id: str,
    payload: AircraftStatusUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(UserRole.MAINTENANCE)),
) -> Aircraft:
    aircraft = db.get(Aircraft, aircraft_id)
    if aircraft is None:
        raise api_error(404, f"Aircraft {aircraft_id} not found")

    aircraft.status = payload.status
    aircraft.source = "manual"
    aircraft.source_ts = datetime.now(UTC)
    aircraft.fused_ts = aircraft.source_ts

    db.commit()
    db.refresh(aircraft)
    return aircraft
