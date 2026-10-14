from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.aircraft_type import AircraftType
from app.schemas.aircraft_type import AircraftTypeRead

router = APIRouter(prefix="/aircraft-types", tags=["aircraft-types"])


@router.get("", response_model=list[AircraftTypeRead])
def list_aircraft_types(
    db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> list[AircraftType]:
    return list(db.scalars(select(AircraftType).order_by(AircraftType.code)))
