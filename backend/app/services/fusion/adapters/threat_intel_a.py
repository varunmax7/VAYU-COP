import random
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.threat import ThreatZone
from app.services.fusion.adapters.base import SourceAdapter

THEATRE_BOUNDS = {"min_lat": 17.5, "max_lat": 25.5, "min_lon": 74.0, "max_lon": 84.0}


class ThreatIntelAAdapter(SourceAdapter):
    """Threat Intel A: decimal coordinates, confidence already on a 0-1 scale."""

    name = "threat_intel_a"
    interval_s = 60.0

    def generate(self, db: Session, rng: random.Random, now: datetime) -> list[dict]:
        zones = list(db.scalars(select(ThreatZone)))
        records = []

        for zone in zones:
            if rng.random() < 0.5:  # not every sensor sees every zone every tick
                continue
            jitter = rng.uniform(-0.02, 0.02)
            records.append(
                {
                    "id_hint": zone.label,
                    "lat": round(zone.center_lat + jitter, 4),
                    "lon": round(zone.center_lon + jitter, 4),
                    "level": zone.level,
                    "conf": round(rng.uniform(0.75, 0.95), 2),
                    "ts_utc": now.isoformat(),
                }
            )

        if rng.random() < 0.01:
            records.append(
                {
                    "id_hint": f"NEW-{rng.randint(100, 999)}",
                    "lat": round(
                        rng.uniform(THEATRE_BOUNDS["min_lat"], THEATRE_BOUNDS["max_lat"]), 4
                    ),
                    "lon": round(
                        rng.uniform(THEATRE_BOUNDS["min_lon"], THEATRE_BOUNDS["max_lon"]), 4
                    ),
                    "level": rng.choice(["LOW", "MED", "HIGH"]),
                    "conf": round(rng.uniform(0.6, 0.9), 2),
                    "ts_utc": datetime.now(UTC).isoformat(),
                }
            )
        return records
