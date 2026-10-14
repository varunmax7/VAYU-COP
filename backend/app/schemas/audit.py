from datetime import datetime

from app.schemas.common import CamelModel


class AuditEntryRead(CamelModel):
    id: str
    ts: datetime
    user_id: str
    role: str
    action: str
    entity_kind: str
    entity_id: str
    before: dict | None
    after: dict | None
    reason: str | None
    prev_hash: str
    hash: str
