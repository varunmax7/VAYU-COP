import random
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.aircraft import Aircraft
from app.models.enums import AircraftStatus
from app.services.fusion.adapters.base import SourceAdapter
from app.services.fusion.normaliser import MAINT_STATUS_CODES
from app.services.fusion.time_utils import IST_OFFSET

_REVERSE_STATUS_CODES = {v: k for k, v in MAINT_STATUS_CODES.items()}


class MaintMisAdapter(SourceAdapter):
    """Maint-MIS: CSV-style dict rows, tail numbers like "KB-604", IST local time strings."""

    name = "maint_mis"
    interval_s = 30.0

    def generate(self, db: Session, rng: random.Random, now: datetime) -> list[dict]:
        aircraft = list(db.scalars(select(Aircraft)))
        if not aircraft:
            return []

        sample = rng.sample(aircraft, k=min(3, len(aircraft)))
        records = []
        for ac in sample:
            status = ac.status
            snag = None
            # Rare chance of a fresh snag grounding a currently-ready airframe.
            if status == AircraftStatus.READY and rng.random() < 0.01:
                status = AircraftStatus.UNSERVICEABLE
                snag = rng.choice(["HYD LEAK", "AVIONICS FAULT", "ENGINE VIBRATION"])

            ts_ist = now + IST_OFFSET
            records.append(
                {
                    "tail": ac.tail_number,
                    "status_code": _REVERSE_STATUS_CODES.get(status, status),
                    "snag": snag,
                    "ts_ist": ts_ist.strftime("%d-%m-%Y %H:%M:%S"),
                    "hours_since_maint": round(ac.hours_since_maint, 1),
                    "hours_to_next_maint": round(ac.hours_to_next_maint, 1),
                }
            )
        return records
