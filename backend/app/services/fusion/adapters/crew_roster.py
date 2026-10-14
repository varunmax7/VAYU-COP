import random
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.crew import CrewMember
from app.models.enums import CrewStatus
from app.services.fusion.adapters.base import SourceAdapter
from app.services.fusion.crosswalk import synthetic_service_number
from app.services.fusion.normaliser import CREW_STATUS_CODES
from app.services.fusion.time_utils import IST_OFFSET

_REVERSE_STATUS_CODES = {v: k for k, v in CREW_STATUS_CODES.items()}


class CrewRosterAdapter(SourceAdapter):
    """Crew Roster: JSON with service numbers, duty times in IST, "rest_ok": "Y"/"N"."""

    name = "crew_roster"
    interval_s = 45.0

    def generate(self, db: Session, rng: random.Random, now: datetime) -> list[dict]:
        crew = list(db.scalars(select(CrewMember)))
        if not crew:
            return []

        sample = rng.sample(crew, k=min(5, len(crew)))
        records = []
        for member in sample:
            service_number = synthetic_service_number(member.id)
            duty_start_ist = (member.duty_start + IST_OFFSET) if member.duty_start else None
            ts_ist = now + IST_OFFSET
            records.append(
                {
                    "svc_no": service_number,
                    "status_code": _REVERSE_STATUS_CODES.get(member.status, member.status),
                    "duty_start_ist": (
                        duty_start_ist.strftime("%d-%m-%Y %H:%M:%S") if duty_start_ist else None
                    ),
                    "duty_hours_24h": member.duty_hours_24h,
                    "rest_ok": "N" if member.status == CrewStatus.RESTING else "Y",
                    "ts_ist": ts_ist.strftime("%d-%m-%Y %H:%M:%S"),
                }
            )
        return records
