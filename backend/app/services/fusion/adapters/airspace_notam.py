import random
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.airspace import Airspace
from app.services.fusion.adapters.base import SourceAdapter


class AirspaceNotamAdapter(SourceAdapter):
    """Airspace/NOTAM: NOTAM-like text, e.g. "AIRSPACE OSCAR CLOSED 1315Z-1800Z"."""

    name = "airspace_notam"
    interval_s = 90.0

    def generate(self, db: Session, rng: random.Random, now: datetime) -> list[dict]:
        airspaces = list(db.scalars(select(Airspace)))
        if not airspaces:
            return []

        sample = rng.sample(airspaces, k=min(2, len(airspaces)))
        records = []
        for a in sample:
            if a.active_from and a.active_to:
                window = f" {a.active_from.strftime('%H%M')}Z-{a.active_to.strftime('%H%M')}Z"
            else:
                window = ""
            records.append({"notam": f"AIRSPACE {a.name} {a.status}{window}"})
        return records
