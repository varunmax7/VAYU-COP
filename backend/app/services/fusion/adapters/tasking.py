import random
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.services.fusion.adapters.base import SourceAdapter
from app.services.fusion.adapters.threat_intel_a import THEATRE_BOUNDS

_TYPES = ["CAP", "RECCE", "STRIKE", "AIRLIFT", "TANKER", "AEW", "SAR", "HADR"]
_PRIORITIES = ["P2_IMMEDIATE", "P3_PRIORITY", "P4_ROUTINE"]


class TaskingAdapter(SourceAdapter):
    """Tasking: mission-request JSON from the UI or a scripted injector."""

    name = "tasking"
    interval_s = 180.0

    def generate(self, db: Session, rng: random.Random, now: datetime) -> list[dict]:
        if rng.random() >= 0.02:
            return []

        mission_type = rng.choice(_TYPES)
        start = now + timedelta(minutes=rng.randint(10, 60))
        name = rng.choice(["SILVER", "VIGIL", "COBRA", "TEMPEST"])
        return [
            {
                "code": f"OP {name} {rng.randint(1, 99)}",
                "type": mission_type,
                "priority": rng.choice(_PRIORITIES),
                "area_name": f"S{rng.randint(1, 12)}",
                "lat": round(rng.uniform(THEATRE_BOUNDS["min_lat"], THEATRE_BOUNDS["max_lat"]), 4),
                "lon": round(rng.uniform(THEATRE_BOUNDS["min_lon"], THEATRE_BOUNDS["max_lon"]), 4),
                "earliest_start": start.isoformat(),
                "latest_start": (start + timedelta(minutes=15)).isoformat(),
                "on_station_min": rng.choice([30, 45, 60, 90]),
                "required_aircraft": 1,
                "required_store": None,
                "ts_utc": datetime.now(UTC).isoformat(),
            }
        ]
