import random
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.aircraft import Aircraft
from app.models.enums import AircraftStatus
from app.services.fusion.adapters.base import SourceAdapter
from app.services.fusion.crosswalk import synthetic_icao24


class TrackFeedAdapter(SourceAdapter):
    """Track Feed: ADS-B-like position messages at 1 Hz, {icao24, lat, lon, alt, gs, trk}."""

    name = "track_feed"
    interval_s = 1.0

    def generate(self, db: Session, rng: random.Random, now: datetime) -> list[dict]:
        aircraft = list(db.scalars(select(Aircraft)))
        records = []
        for ac in aircraft:
            # No flight-dynamics simulation yet (that's Phase 9's sim engine) — parked
            # aircraft get tiny GPS-noise jitter so the feed still looks "live" at 1 Hz.
            is_airborne = ac.status == AircraftStatus.AIRBORNE
            jitter = rng.uniform(-0.0003, 0.0003) if is_airborne else rng.uniform(-0.00003, 0.00003)
            records.append(
                {
                    "icao24": synthetic_icao24(ac.id),
                    "lat": round(ac.lat + jitter, 6),
                    "lon": round(ac.lon + jitter, 6),
                    "alt_ft": ac.alt_ft,
                    "gs_kt": ac.speed_kts,
                    "trk_deg": ac.heading_deg,
                    "ts_utc": now.isoformat(),
                }
            )
        return records
