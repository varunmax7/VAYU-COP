import random
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.threat import ThreatZone
from app.services.fusion.adapters.base import SourceAdapter
from app.services.fusion.adapters.threat_intel_a import THEATRE_BOUNDS
from app.services.fusion.time_utils import decimal_to_dms


class ThreatIntelBAdapter(SourceAdapter):
    """Threat Intel B: DMS coordinates, confidence on a 1-5 scale."""

    name = "threat_intel_b"
    interval_s = 65.0

    def generate(self, db: Session, rng: random.Random, now: datetime) -> list[dict]:
        zones = list(db.scalars(select(ThreatZone)))
        records = []

        for zone in zones:
            if rng.random() < 0.5:
                continue
            jitter = rng.uniform(-0.02, 0.02)
            records.append(
                {
                    "id_hint": zone.label,
                    "lat_dms": decimal_to_dms(zone.center_lat + jitter, is_latitude=True),
                    "lon_dms": decimal_to_dms(zone.center_lon + jitter, is_latitude=False),
                    "level": zone.level,
                    "conf_5": rng.randint(3, 5),
                    "ts_utc": now.isoformat(),
                }
            )

        if rng.random() < 0.01:
            lat = rng.uniform(THEATRE_BOUNDS["min_lat"], THEATRE_BOUNDS["max_lat"])
            lon = rng.uniform(THEATRE_BOUNDS["min_lon"], THEATRE_BOUNDS["max_lon"])
            records.append(
                {
                    "id_hint": f"NEW-{rng.randint(100, 999)}",
                    "lat_dms": decimal_to_dms(lat, is_latitude=True),
                    "lon_dms": decimal_to_dms(lon, is_latitude=False),
                    "level": rng.choice(["LOW", "MED", "HIGH"]),
                    "conf_5": rng.randint(3, 5),
                    "ts_utc": datetime.now(UTC).isoformat(),
                }
            )
        return records
