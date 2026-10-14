import json
from pathlib import Path

import pytest
from app.core.db import SessionLocal
from app.models.aircraft import Aircraft
from app.models.base import AirBase
from app.models.crew import CrewMember
from app.models.mission import Mission
from app.models.stores import StoreInventory
from app.models.threat import ThreatZone
from app.models.user import User
from app.seed.generator import run as run_seed
from app.seed.scenario_schema import Scenario

THEATRE = {"min_lat": 17.5, "max_lat": 25.5, "min_lon": 74.0, "max_lon": 84.0}


@pytest.fixture(scope="module", autouse=True)
def fresh_seed():
    """Other test modules (e.g. test_rbac.py) write rows through the API, so re-seed
    immediately before this module's exact-count assertions run."""
    run_seed(scenario_name="vayu_shield", do_reset=True)


def _in_theatre(lat: float, lon: float) -> bool:
    return (
        THEATRE["min_lat"] <= lat <= THEATRE["max_lat"]
        and THEATRE["min_lon"] <= lon <= THEATRE["max_lon"]
    )


def test_entity_counts():
    db = SessionLocal()
    try:
        assert db.query(AirBase).count() == 4
        assert db.query(Aircraft).count() == 42
        assert db.query(ThreatZone).count() == 3
        assert db.query(User).count() == 7
        top_level_missions = db.query(Mission).filter(Mission.parent_id.is_(None)).count()
        assert top_level_missions == 12
        crew_count = db.query(CrewMember).count()
        assert 100 <= crew_count <= 150
    finally:
        db.close()


def test_every_aircraft_at_a_valid_base():
    db = SessionLocal()
    try:
        base_ids = {b.id for b in db.query(AirBase).all()}
        for aircraft in db.query(Aircraft).all():
            assert aircraft.base_id in base_ids
            assert _in_theatre(aircraft.lat, aircraft.lon)
    finally:
        db.close()


def test_every_crew_qualified_on_a_type_present_at_their_base():
    db = SessionLocal()
    try:
        types_by_base: dict[str, set[str]] = {}
        for aircraft in db.query(Aircraft).all():
            types_by_base.setdefault(aircraft.base_id, set()).add(aircraft.type_code)

        for crew in db.query(CrewMember).all():
            hosted_types = types_by_base.get(crew.base_id, set())
            assert set(crew.qualified_types) & hosted_types, (
                f"{crew.id} at {crew.base_id} is qualified on {crew.qualified_types} "
                f"but that base only hosts {hosted_types}"
            )
    finally:
        db.close()


def test_coordinates_inside_theatre_box():
    db = SessionLocal()
    try:
        for base in db.query(AirBase).all():
            assert _in_theatre(base.lat, base.lon), base.id
        for threat in db.query(ThreatZone).all():
            assert _in_theatre(threat.center_lat, threat.center_lon), threat.id
    finally:
        db.close()


def test_mission_windows_valid():
    db = SessionLocal()
    try:
        missions = db.query(Mission).all()
        assert len(missions) > 0
        for mission in missions:
            assert mission.earliest_start <= mission.latest_start
            assert mission.on_station_min > 0
            assert mission.required_aircraft >= 0
            if mission.parent_id is not None:
                parent = db.get(Mission, mission.parent_id)
                assert parent is not None
    finally:
        db.close()


def test_store_inventory_non_negative():
    db = SessionLocal()
    try:
        for store in db.query(StoreInventory).all():
            assert store.available >= 0
            assert store.reserved >= 0
    finally:
        db.close()


def test_scenario_json_validates_against_schema():
    path = Path(__file__).resolve().parents[1] / "app" / "seed" / "scenarios" / "vayu_shield.json"
    data = json.loads(path.read_text())
    scenario = Scenario.model_validate(data)
    assert scenario.seed == 26250
    assert len(scenario.bases) == 4
    assert len(scenario.missions) == 12
    assert sum(a.qty for t in scenario.aircraft_types for a in t.allocations) == 42
