from datetime import datetime

from app.models.enums import AlertSeverity
from app.schemas.common import CamelModel


class EventRead(CamelModel):
    id: str
    ts: datetime
    sim_ts: datetime
    source: str
    type: str
    severity: AlertSeverity
    payload: dict
    processed: bool
