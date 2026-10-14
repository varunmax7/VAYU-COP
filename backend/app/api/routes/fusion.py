from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, require_roles
from app.core.errors import api_error
from app.models.enums import UserRole
from app.schemas.fusion import FusionSourceRead, FusionSourceUpdate
from app.services.fusion.engine import fusion_engine

router = APIRouter(prefix="/fusion", tags=["fusion"])


@router.get("/sources", response_model=list[FusionSourceRead])
def list_sources(_user=Depends(get_current_user)) -> list[FusionSourceRead]:
    sources = []
    for name, health in fusion_engine.source_health().items():
        lag = health.lag_s
        sources.append(
            FusionSourceRead(
                name=name,
                enabled=health.enabled,
                status=health.status,
                last_msg_ts=health.last_msg_ts,
                msgs_per_min=health.msgs_per_min,
                errors=health.errors,
                lag_s=None if lag == float("inf") else round(lag, 1),
            )
        )
    return sorted(sources, key=lambda s: s.name)


@router.patch("/sources/{name}", response_model=FusionSourceRead)
def toggle_source(
    name: str,
    payload: FusionSourceUpdate,
    _user=Depends(require_roles(UserRole.ADMIN)),
) -> FusionSourceRead:
    if not fusion_engine.set_enabled(name, payload.enabled):
        raise api_error(404, f"Unknown fusion source {name!r}")
    health = fusion_engine.source_health()[name]
    lag = health.lag_s
    return FusionSourceRead(
        name=name,
        enabled=health.enabled,
        status=health.status,
        last_msg_ts=health.last_msg_ts,
        msgs_per_min=health.msgs_per_min,
        errors=health.errors,
        lag_s=None if lag == float("inf") else round(lag, 1),
    )
