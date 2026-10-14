from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.core.errors import api_error
from app.models.airspace import Airspace
from app.models.enums import UserRole
from app.schemas.airspace import AirspaceRead, AirspaceUpdate

router = APIRouter(prefix="/airspace", tags=["airspace"])


@router.get("", response_model=list[AirspaceRead])
def list_airspace(db: Session = Depends(get_db), _user=Depends(get_current_user)) -> list[Airspace]:
    return list(db.scalars(select(Airspace).order_by(Airspace.id)))


@router.patch("/{airspace_id}", response_model=AirspaceRead)
def update_airspace(
    airspace_id: str,
    payload: AirspaceUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(UserRole.PLANNER, UserRole.ADMIN)),
) -> Airspace:
    airspace = db.get(Airspace, airspace_id)
    if airspace is None:
        raise api_error(404, f"Airspace {airspace_id} not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(airspace, field, value)

    db.commit()
    db.refresh(airspace)
    return airspace
