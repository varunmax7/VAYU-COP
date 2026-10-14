from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.core.errors import api_error
from app.models.base import AirBase
from app.models.enums import UserRole
from app.schemas.base import AirBaseRead, AirBaseUpdate

router = APIRouter(prefix="/bases", tags=["bases"])


@router.get("", response_model=list[AirBaseRead])
def list_bases(db: Session = Depends(get_db), _user=Depends(get_current_user)) -> list[AirBase]:
    return list(db.scalars(select(AirBase).order_by(AirBase.id)))


@router.get("/{base_id}", response_model=AirBaseRead)
def get_base(
    base_id: str, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> AirBase:
    base = db.get(AirBase, base_id)
    if base is None:
        raise api_error(404, f"Base {base_id} not found")
    return base


@router.patch("/{base_id}", response_model=AirBaseRead)
def update_base(
    base_id: str,
    payload: AirBaseUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(UserRole.COMMANDER, UserRole.ADMIN)),
) -> AirBase:
    base = db.get(AirBase, base_id)
    if base is None:
        raise api_error(404, f"Base {base_id} not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(base, field, value)

    db.commit()
    db.refresh(base)
    return base
