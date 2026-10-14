import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy.orm import Session


@dataclass
class SourceHealth:
    name: str
    interval_s: float
    enabled: bool = True
    last_msg_ts: datetime | None = None
    errors: int = 0
    _window_count: int = 0
    _window_start: datetime = field(default_factory=lambda: datetime.now(UTC))
    msgs_per_min: float = 0.0

    def record_message(self, now: datetime, count: int = 1) -> None:
        self.last_msg_ts = now
        self._window_count += count
        elapsed = (now - self._window_start).total_seconds()
        if elapsed >= 60:
            self.msgs_per_min = round(self._window_count / (elapsed / 60), 1)
            self._window_count = 0
            self._window_start = now

    def record_error(self) -> None:
        self.errors += 1

    @property
    def lag_s(self) -> float:
        if self.last_msg_ts is None:
            return float("inf")
        return (datetime.now(UTC) - self.last_msg_ts).total_seconds()

    @property
    def status(self) -> str:
        if not self.enabled:
            return "DOWN"
        lag = self.lag_s
        if lag <= self.interval_s * 3:
            return "OK"
        if lag <= self.interval_s * 10:
            return "DEGRADED"
        return "DOWN"


class SourceAdapter(ABC):
    name: str
    interval_s: float

    def __init__(self) -> None:
        self.health = SourceHealth(name=self.name, interval_s=self.interval_s)

    @abstractmethod
    def generate(self, db: Session, rng: random.Random, now: datetime) -> list[dict]:
        """Produces zero or more raw, native-format records for one tick."""
        raise NotImplementedError
