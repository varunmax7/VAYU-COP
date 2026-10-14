from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.weather import WeatherCell, WeatherObs
from app.schemas.weather import WeatherCellRead, WeatherObsRead

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/bases", response_model=list[WeatherObsRead])
def latest_base_weather(
    db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> list[WeatherObs]:
    """Latest non-forecast observation per base. Populated by the Phase 3 fusion adapters."""
    stmt = (
        select(WeatherObs)
        .where(WeatherObs.is_forecast.is_(False))
        .order_by(WeatherObs.base_id, WeatherObs.valid_ts.desc())
    )
    rows = list(db.scalars(stmt))
    seen: set[str] = set()
    latest: list[WeatherObs] = []
    for obs in rows:
        if obs.base_id not in seen:
            seen.add(obs.base_id)
            latest.append(obs)
    return latest


@router.get("/cells", response_model=list[WeatherCellRead])
def list_weather_cells(
    db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> list[WeatherCell]:
    return list(db.scalars(select(WeatherCell).order_by(WeatherCell.id)))


@router.get("/forecast/{base_id}", response_model=list[WeatherObsRead])
def base_forecast(
    base_id: str, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> list[WeatherObs]:
    """Hourly forecast for a base. Populated by the Phase 3 Open-Meteo/synthetic adapter."""
    stmt = (
        select(WeatherObs)
        .where(WeatherObs.base_id == base_id, WeatherObs.is_forecast.is_(True))
        .order_by(WeatherObs.valid_ts)
    )
    return list(db.scalars(stmt))
