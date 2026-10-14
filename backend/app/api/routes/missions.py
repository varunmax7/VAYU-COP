import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.core.errors import api_error
from app.models.enums import MissionStatus, UserRole
from app.models.mission import Mission
from app.schemas.mission import MissionCreate, MissionRead, MissionUpdate

router = APIRouter(prefix="/missions", tags=["missions"])


@router.get("", response_model=list[MissionRead])
def list_missions(
    status_: MissionStatus | None = Query(None, alias="status"),
    priority: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[Mission]:
    stmt = select(Mission)
    if status_:
        stmt = stmt.where(Mission.status == status_)
    if priority:
        stmt = stmt.where(Mission.priority == priority)
    stmt = stmt.order_by(Mission.id).offset(offset).limit(limit)
    return list(db.scalars(stmt))


@router.post("", response_model=MissionRead, status_code=status.HTTP_201_CREATED)
def create_mission(
    payload: MissionCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(UserRole.PLANNER, UserRole.COMMANDER)),
) -> Mission:
    mission = Mission(id=f"MISSION-{uuid.uuid4().hex[:8].upper()}", **payload.model_dump())
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return mission


@router.get("/{mission_id}", response_model=MissionRead)
def get_mission(
    mission_id: str, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> Mission:
    mission = db.get(Mission, mission_id)
    if mission is None:
        raise api_error(404, f"Mission {mission_id} not found")
    return mission


@router.patch("/{mission_id}", response_model=MissionRead)
def update_mission(
    mission_id: str,
    payload: MissionUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(UserRole.PLANNER, UserRole.COMMANDER)),
) -> Mission:
    mission = db.get(Mission, mission_id)
    if mission is None:
        raise api_error(404, f"Mission {mission_id} not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(mission, field, value)

    db.commit()
    db.refresh(mission)
    return mission


@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mission(
    mission_id: str,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(UserRole.PLANNER, UserRole.COMMANDER)),
) -> None:
    mission = db.get(Mission, mission_id)
    if mission is None:
        raise api_error(404, f"Mission {mission_id} not found")

    for child in db.scalars(select(Mission).where(Mission.parent_id == mission_id)):
        db.delete(child)
    db.delete(mission)
    db.commit()
