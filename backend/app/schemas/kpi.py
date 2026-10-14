from datetime import datetime

from app.schemas.common import CamelModel


class KpisRead(CamelModel):
    aircraft_ready: int
    aircraft_total: int
    active_sorties: int
    crew_currency_pct: float
    critical_alerts: int
    ai_confidence_pct: float | None
    zulu_time: datetime
