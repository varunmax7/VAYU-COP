from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.core.errors import api_error
from app.models.crew import CrewMember
from app.models.enums import CrewStatus, UserRole
from app.schemas.crew import CrewMemberRead, CrewStatusUpdate

router = APIRouter(prefix="/crew", tags=["crew"])


@router.get("", response_model=list[CrewMemberRead])
def list_crew(
    base: str | None = None,
    type: str | None = None,
    status: CrewStatus | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[CrewMember]:
    stmt = select(CrewMember)
    if base:
        stmt = stmt.where(CrewMember.base_id == base)
    if status:
        stmt = stmt.where(CrewMember.status == status)
    stmt = stmt.order_by(CrewMember.id)

    rows = list(db.scalars(stmt))
    # qualified_types is a JSON list column — membership filtering stays in Python
    # so this works identically on SQLite (dev) and Postgres (prod) without dialect-specific SQL.
    if type:
        rows = [c for c in rows if type in c.qualified_types]
    return rows[offset : offset + limit]


@router.patch("/{crew_id}/status", response_model=CrewMemberRead)
def update_crew_status(
    crew_id: str,
    payload: CrewStatusUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(UserRole.PLANNER, UserRole.ADMIN)),
) -> CrewMember:
    crew = db.get(CrewMember, crew_id)
    if crew is None:
        raise api_error(404, f"Crew member {crew_id} not found")

    crew.status = payload.status
    db.commit()
    db.refresh(crew)
    return crew
