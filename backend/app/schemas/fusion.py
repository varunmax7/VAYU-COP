from datetime import datetime

from app.schemas.common import CamelModel


class FusionSourceRead(CamelModel):
    name: str
    enabled: bool
    status: str  # OK | DEGRADED | DOWN
    last_msg_ts: datetime | None
    msgs_per_min: float
    errors: int
    lag_s: float | None


class FusionSourceUpdate(CamelModel):
    enabled: bool
