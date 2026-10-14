from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.kpi import KpisRead
from app.services.kpi_service import compute_kpis

router = APIRouter(tags=["kpis"])


@router.get("/kpis", response_model=KpisRead)
def get_kpis(db: Session = Depends(get_db), _user=Depends(get_current_user)) -> KpisRead:
    return compute_kpis(db)
