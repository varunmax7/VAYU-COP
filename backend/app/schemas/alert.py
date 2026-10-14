from datetime import datetime

from app.models.enums import AlertSeverity
from app.schemas.common import CamelModel


class AlertRead(CamelModel):
    id: str
    ts: datetime
    severity: AlertSeverity
    category: str
    message: str
    entity_refs: list[dict]
    dedup_key: str
    acknowledged_by: str | None
    acknowledged_at: datetime | None
    resolved: bool
    resolved_at: datetime | None
