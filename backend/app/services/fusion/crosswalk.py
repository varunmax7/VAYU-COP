"""Maps native source identifiers (tail numbers, ADS-B icao24 hex, service numbers) to
canonical entity IDs (§8.2 step 2). Built once from the DB; synthetic icao24/service numbers
are derived deterministically from canonical IDs so adapters and the crosswalk always agree."""

import hashlib

from sqlalchemy.orm import Session

from app.models.aircraft import Aircraft
from app.models.crew import CrewMember


def synthetic_icao24(aircraft_id: str) -> str:
    return hashlib.sha1(aircraft_id.encode()).hexdigest()[:6].upper()


def synthetic_service_number(crew_id: str) -> str:
    return "IC-" + hashlib.sha1(crew_id.encode()).hexdigest()[:5].upper()


class CrosswalkRegistry:
    def __init__(self) -> None:
        self._tail_to_aircraft: dict[str, str] = {}
        self._icao24_to_aircraft: dict[str, str] = {}
        self._service_number_to_crew: dict[str, str] = {}

    def refresh(self, db: Session) -> None:
        self._tail_to_aircraft.clear()
        self._icao24_to_aircraft.clear()
        self._service_number_to_crew.clear()

        for aircraft in db.query(Aircraft).all():
            self._tail_to_aircraft[aircraft.tail_number] = aircraft.id
            self._icao24_to_aircraft[synthetic_icao24(aircraft.id)] = aircraft.id

        for crew in db.query(CrewMember).all():
            self._service_number_to_crew[synthetic_service_number(crew.id)] = crew.id

    def aircraft_id_for_tail(self, tail_number: str) -> str | None:
        return self._tail_to_aircraft.get(tail_number)

    def aircraft_id_for_icao24(self, icao24: str) -> str | None:
        return self._icao24_to_aircraft.get(icao24)

    def crew_id_for_service_number(self, service_number: str) -> str | None:
        return self._service_number_to_crew.get(service_number)

    def all_aircraft_icao24(self) -> dict[str, str]:
        """{icao24: aircraft_id} for every aircraft — adapters use this to emit track_feed."""
        return dict(self._icao24_to_aircraft)

    def all_crew_service_numbers(self) -> dict[str, str]:
        """{service_number: crew_id} for every crew member — adapters use this for crew_roster."""
        return dict(self._service_number_to_crew)


crosswalk = CrosswalkRegistry()
