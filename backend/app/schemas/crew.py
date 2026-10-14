from datetime import datetime

from app.models.enums import CrewRole, CrewStatus
from app.schemas.common import CamelModel, ProvenanceRead


class CrewMemberRead(ProvenanceRead):
    id: str
    name: str
    rank: str
    role: CrewRole
    base_id: str
    qualified_types: list[str]
    currency_expiry: dict[str, str]
    status: CrewStatus
    duty_start: datetime | None
    duty_hours_24h: float
    duty_hours_7d: float
    last_rest_end: datetime | None
    fatigue_score: float


class CrewStatusUpdate(CamelModel):
    status: CrewStatus
