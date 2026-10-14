"""Builds the reproducible "VAYU SHIELD" exercise world (§7) into the configured database.

Bases, aircraft types, airspace, threats, weather cells and mission requests come straight
from the scenario JSON (seed/scenarios/<name>.json). Aircraft, crew, store inventory and users
are generated with a seeded RNG so the same `--scenario` always produces the same world.
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.db import Base as DbBase
from app.core.db import SessionLocal, engine
from app.core.security import hash_password
from app.models.aircraft import Aircraft
from app.models.aircraft_type import AircraftType
from app.models.airspace import Airspace
from app.models.base import AirBase
from app.models.crew import CrewMember
from app.models.enums import (
    AircraftStatus,
    CrewStatus,
    UserRole,
)
from app.models.mission import Mission
from app.models.stores import StoreInventory
from app.models.threat import ThreatZone
from app.models.user import User
from app.models.weather import WeatherCell
from app.seed.scenario_schema import Scenario

SCENARIOS_DIR = Path(__file__).parent / "scenarios"

RANKS = ["Fg Offr", "Flt Lt", "Sqn Ldr", "Wg Cdr", "Gp Capt"]
RANK_WEIGHTS = [0.30, 0.30, 0.22, 0.12, 0.06]

FIRST_NAMES = [
    "Aarav",
    "Vihaan",
    "Arjun",
    "Ishaan",
    "Rohan",
    "Karan",
    "Siddharth",
    "Aditya",
    "Rahul",
    "Vikram",
    "Sanjay",
    "Ananya",
    "Diya",
    "Kavya",
    "Priya",
    "Neha",
    "Pooja",
    "Riya",
    "Shreya",
    "Meera",
    "Nikhil",
    "Varun",
    "Abhishek",
    "Gaurav",
    "Deepika",
    "Sunita",
    "Rajesh",
    "Manoj",
    "Suresh",
    "Anil",
    "Kiran",
    "Ravi",
    "Harish",
    "Naveen",
    "Pradeep",
    "Vivek",
    "Ajay",
    "Sameer",
    "Tarun",
    "Yash",
]
LAST_NAMES = [
    "Sharma",
    "Verma",
    "Gupta",
    "Mehta",
    "Rao",
    "Nair",
    "Menon",
    "Iyer",
    "Reddy",
    "Patel",
    "Kulkarni",
    "Joshi",
    "Chauhan",
    "Malhotra",
    "Kapoor",
    "Bhatia",
    "Choudhary",
    "Desai",
    "Pillai",
    "Saxena",
    "Agarwal",
    "Bose",
    "Chatterjee",
    "Das",
    "Gill",
    "Khanna",
    "Mishra",
    "Pandey",
    "Singh",
    "Thakur",
]

STATUS_TARGETS = {
    AircraftStatus.READY: 0.78,
    AircraftStatus.MAINTENANCE: 0.10,
    AircraftStatus.UNSERVICEABLE: 0.05,
    AircraftStatus.TURNAROUND: 0.07,
}


def _square_polygon(center_lat: float, center_lon: float, half_width_deg: float) -> dict:
    lat0, lat1 = center_lat - half_width_deg, center_lat + half_width_deg
    lon0, lon1 = center_lon - half_width_deg, center_lon + half_width_deg
    ring = [[lon0, lat0], [lon1, lat0], [lon1, lat1], [lon0, lat1], [lon0, lat0]]
    return {"type": "Polygon", "coordinates": [ring]}


def _latlon_ring_to_geojson(ring: list[list[float]]) -> dict:
    coords = [[lon, lat] for lat, lon in ring]
    return {"type": "Polygon", "coordinates": [coords]}


def load_scenario(name: str) -> Scenario:
    path = SCENARIOS_DIR / f"{name}.json"
    data = json.loads(path.read_text())
    return Scenario.model_validate(data)


def reset_schema() -> None:
    DbBase.metadata.drop_all(bind=engine)
    DbBase.metadata.create_all(bind=engine)


def _status_assignments(rng: random.Random, n: int) -> list[AircraftStatus]:
    counts = {status: round(n * pct) for status, pct in STATUS_TARGETS.items()}
    # rounding can drift the total; correct against READY
    drift = n - sum(counts.values())
    counts[AircraftStatus.READY] += drift
    statuses: list[AircraftStatus] = []
    for status, count in counts.items():
        statuses.extend([status] * count)
    rng.shuffle(statuses)
    return statuses


def seed_bases(db: Session, scenario: Scenario, now: datetime) -> dict[str, AirBase]:
    bases: dict[str, AirBase] = {}
    for b in scenario.bases:
        base = AirBase(
            id=b.id,
            name=b.name,
            code=b.code,
            lat=b.lat,
            lon=b.lon,
            runways=b.runways,
            runway_capacity_per_15min=b.runway_capacity_per_15min,
            parking_capacity=b.parking_capacity,
            fuel_stock_kl=b.fuel_stock_kl,
            closures=[],
        )
        db.add(base)
        bases[base.id] = base
    return bases


def seed_aircraft_types(db: Session, scenario: Scenario) -> dict[str, AircraftType]:
    types: dict[str, AircraftType] = {}
    for t in scenario.aircraft_types:
        at = AircraftType(
            code=t.code,
            name=t.name,
            roles=t.roles,
            cruise_kts=t.cruise_kts,
            range_km=t.range_km,
            endurance_h=t.endurance_h,
            turnaround_min=t.turnaround_min,
            crew_required=t.crew_required,
            compatible_stores=t.compatible_stores,
            wx_minima=t.wx_minima,
        )
        db.add(at)
        types[at.code] = at
    return types


def seed_airspace(db: Session, scenario: Scenario, now: datetime) -> None:
    for a in scenario.airspaces:
        db.add(
            Airspace(
                id=a.id,
                name=a.name,
                kind=a.kind,
                polygon_geojson=_latlon_ring_to_geojson(a.polygon_lat_lon),
                floor_ft=a.floor_ft,
                ceiling_ft=a.ceiling_ft,
                status=a.status,
                source="airspace_notam",
                source_ts=now,
                fused_ts=now,
                confidence=1.0,
                stale=False,
            )
        )


def seed_threats(db: Session, scenario: Scenario, now: datetime) -> None:
    for t in scenario.threats:
        db.add(
            ThreatZone(
                id=t.id,
                label=t.label,
                level=t.level,
                center_lat=t.center_lat,
                center_lon=t.center_lon,
                radius_km=t.radius_km,
                mobile=t.mobile,
                first_seen=now,
                last_seen=now,
                sources=t.sources,
                source=t.sources[0] if t.sources else "threat_intel_a",
                source_ts=now,
                fused_ts=now,
                confidence=1.0 if len(t.sources) < 2 else 0.95,
                stale=False,
            )
        )


def seed_weather_cells(db: Session, scenario: Scenario) -> None:
    for w in scenario.weather_cells:
        db.add(
            WeatherCell(
                id=w.id,
                label=w.label,
                center_lat=w.center_lat,
                center_lon=w.center_lon,
                radius_km=w.radius_km,
                severity=w.severity,
                motion_deg=w.motion_deg,
                motion_kts=w.motion_kts,
            )
        )


def seed_missions(db: Session, scenario: Scenario) -> list[Mission]:
    created: list[Mission] = []
    for m in scenario.missions:
        area_geojson = _square_polygon(m.center_lat, m.center_lon, m.half_width_deg)
        earliest = datetime.fromisoformat(m.earliest_start)
        latest = datetime.fromisoformat(m.latest_start)
        mission = Mission(
            id=m.id,
            code=m.code,
            type=m.type,
            priority=m.priority,
            area_geojson=area_geojson,
            area_name=m.area_name,
            earliest_start=earliest,
            latest_start=latest,
            on_station_min=m.on_station_min,
            required_aircraft=m.required_aircraft,
            required_store=m.required_store,
            notes=m.notes,
        )
        db.add(mission)
        created.append(mission)

        if m.relay_slots:
            for i in range(m.relay_slots.count):
                slot_start = earliest + timedelta(minutes=i * m.relay_slots.slot_minutes)
                slot_latest = slot_start + timedelta(minutes=10)
                slot = Mission(
                    id=f"{m.id}-SLOT{i + 1}",
                    code=f"{m.code} SLOT {i + 1}",
                    type=m.type,
                    priority=m.priority,
                    area_geojson=area_geojson,
                    area_name=m.area_name,
                    earliest_start=slot_start,
                    latest_start=slot_latest,
                    on_station_min=m.relay_slots.slot_minutes,
                    required_aircraft=m.relay_slots.aircraft_per_slot,
                    required_store=m.required_store,
                    parent_id=m.id,
                    notes=f"Relay slot {i + 1}/{m.relay_slots.count} of {m.code}",
                )
                db.add(slot)
                created.append(slot)
    return created


def seed_aircraft(
    db: Session, scenario: Scenario, rng: random.Random, now: datetime
) -> list[Aircraft]:
    created: list[Aircraft] = []
    tail_seq = 600
    low_maint_budget = 3  # a few deliberately-low hours_to_next_maint, per §7.2

    # Status mix (§7.2: ~78% READY / 10% MAINTENANCE / 5% U/S / 7% TURNAROUND) is a fleet-wide
    # split. Computing it per aircraft type would round tiny per-type counts almost entirely
    # into READY, so draw one shuffled list across the whole fleet instead.
    total_fleet = sum(a.qty for t in scenario.aircraft_types for a in t.allocations)
    status_iter = iter(_status_assignments(rng, total_fleet))

    for t in scenario.aircraft_types:
        per_type_seq = 0

        for alloc in t.allocations:
            base = next(b for b in scenario.bases if b.id == alloc.base_id)
            for _ in range(alloc.qty):
                per_type_seq += 1
                tail_seq += 1
                status = next(status_iter)

                if low_maint_budget > 0 and rng.random() < 0.15:
                    hours_to_next_maint = rng.uniform(2, 8)
                    low_maint_budget -= 1
                else:
                    hours_to_next_maint = rng.uniform(8, 120)

                p_us = rng.uniform(0.02, 0.08)
                if hours_to_next_maint < 10:
                    p_us = rng.uniform(0.15, 0.40)

                aircraft = Aircraft(
                    id=f"{t.code}-{per_type_seq:02d}",
                    tail_number=f"KB-{tail_seq}",
                    callsign=f"{t.code} #{per_type_seq:02d}",
                    type_code=t.code,
                    base_id=base.id,
                    status=status,
                    fuel_pct=rng.uniform(60, 100),
                    airframe_hours=rng.uniform(500, 8000),
                    hours_since_maint=rng.uniform(0, 150),
                    hours_to_next_maint=hours_to_next_maint,
                    store_config=rng.choice(t.compatible_stores) if t.compatible_stores else None,
                    lat=base.lat,
                    lon=base.lon,
                    heading_deg=0.0,
                    alt_ft=0.0,
                    speed_kts=0.0,
                    current_assignment_id=None,
                    p_unserviceable_24h=round(p_us, 3),
                    source="maint_mis",
                    source_ts=now,
                    fused_ts=now,
                    confidence=1.0,
                    stale=False,
                )
                db.add(aircraft)
                created.append(aircraft)
    return created


def _weighted_role_counts(
    crew_required: dict[str, int], qty: int, multiplier: float
) -> dict[str, int]:
    return {role: max(1, round(qty * count * multiplier)) for role, count in crew_required.items()}


def seed_crew(
    db: Session, scenario: Scenario, rng: random.Random, now: datetime
) -> list[CrewMember]:
    created: list[CrewMember] = []
    seq = 0

    for t in scenario.aircraft_types:
        role_counts = _weighted_role_counts(t.crew_required, sum(a.qty for a in t.allocations), 1.5)
        # Spread each role's crew across the type's bases, weighted by aircraft qty there.
        base_weights = [(a.base_id, a.qty) for a in t.allocations]
        bases_pool = [b for b, qty in base_weights for _ in range(qty)]

        for role, count in role_counts.items():
            for _ in range(count):
                seq += 1
                base_id = rng.choice(bases_pool)
                roll = rng.random()
                if roll < 0.05:
                    status = rng.choice([CrewStatus.LEAVE, CrewStatus.MEDICAL])
                else:
                    status = rng.choices(
                        [CrewStatus.AVAILABLE, CrewStatus.ON_DUTY, CrewStatus.RESTING],
                        weights=[0.5, 0.3, 0.2],
                    )[0]

                if rng.random() < 0.10:
                    expiry = now + timedelta(days=rng.uniform(0, 3))
                else:
                    expiry = now + timedelta(days=rng.uniform(4, 180))

                duty_hours_24h = (
                    rng.uniform(0, 11) if status == CrewStatus.ON_DUTY else rng.uniform(0, 4)
                )
                fatigue = min(100.0, 10 + duty_hours_24h * 4 + rng.uniform(0, 15))

                crew = CrewMember(
                    id=f"CREW-{seq:04d}",
                    name=f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
                    rank=rng.choices(RANKS, weights=RANK_WEIGHTS)[0],
                    role=role,
                    base_id=base_id,
                    qualified_types=[t.code],
                    currency_expiry={t.code: expiry.date().isoformat()},
                    status=status,
                    duty_start=now if status == CrewStatus.ON_DUTY else None,
                    duty_hours_24h=round(duty_hours_24h, 1),
                    duty_hours_7d=round(duty_hours_24h * rng.uniform(2.5, 4.5), 1),
                    last_rest_end=now - timedelta(hours=rng.uniform(0, 20)),
                    fatigue_score=round(fatigue, 1),
                    source="crew_roster",
                    source_ts=now,
                    fused_ts=now,
                    confidence=1.0,
                    stale=False,
                )
                db.add(crew)
                created.append(crew)
    return created


def seed_stores(db: Session, scenario: Scenario, aircraft: list[Aircraft]) -> list[StoreInventory]:
    created: list[StoreInventory] = []
    demand: dict[tuple[str, str], int] = {}
    types_by_code = {t.code: t for t in scenario.aircraft_types}

    for ac in aircraft:
        t = types_by_code[ac.type_code]
        for category in t.compatible_stores:
            key = (ac.base_id, category)
            demand[key] = demand.get(key, 0) + 1

    for (base_id, category), count in sorted(demand.items()):
        available = max(2, round(count * 1.5))
        # Deliberately short Delta's GA_GENERIC, per the STORES_SHORTFALL alert example (§14).
        if base_id == "DELTA" and category == "GA_GENERIC":
            available = max(0, count - 2)
        store = StoreInventory(
            id=f"STORE-{base_id}-{category}",
            base_id=base_id,
            category=category,
            available=available,
            reserved=0,
        )
        db.add(store)
        created.append(store)
    return created


SEED_USERS = [
    ("commander", "commander123", "Commander", UserRole.COMMANDER),
    ("planner", "planner123", "Planner", UserRole.PLANNER),
    ("maint", "maint123", "Maintenance Officer", UserRole.MAINTENANCE),
    ("met", "met123", "Met Officer", UserRole.MET),
    ("intel", "intel123", "Intel Officer", UserRole.INTEL),
    ("crew", "crew123", "Aircrew", UserRole.AIRCREW),
    ("admin", "admin123", "Admin", UserRole.ADMIN),
]


def seed_users(db: Session) -> list[User]:
    created = []
    for username, password, display_name, role in SEED_USERS:
        user = User(
            id=username,
            username=username,
            display_name=display_name,
            role=role,
            password_hash=hash_password(password),
        )
        db.add(user)
        created.append(user)
    return created


def run(scenario_name: str = "vayu_shield", do_reset: bool = True) -> dict[str, int]:
    scenario = load_scenario(scenario_name)
    rng = random.Random(scenario.seed)
    now = datetime.fromisoformat(scenario.sim_start)

    if do_reset:
        reset_schema()

    db = SessionLocal()
    try:
        seed_bases(db, scenario, now)
        seed_aircraft_types(db, scenario)
        db.flush()  # bases/types must exist before aircraft/crew/stores reference them

        seed_airspace(db, scenario, now)
        seed_threats(db, scenario, now)
        seed_weather_cells(db, scenario)
        missions = seed_missions(db, scenario)
        aircraft = seed_aircraft(db, scenario, rng, now)
        crew = seed_crew(db, scenario, rng, now)
        db.flush()  # aircraft must exist before computing store demand

        stores = seed_stores(db, scenario, aircraft)
        users = seed_users(db)

        # Read everything the summary needs while the session is still attached —
        # these become plain ints/lists that survive the session closing below.
        n_relay_slots = sum(1 for m in missions if "-SLOT" in m.id)
        n_aircraft, n_crew, n_stores, n_users = (
            len(aircraft),
            len(crew),
            len(stores),
            len(users),
        )

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return {
        "bases": len(scenario.bases),
        "aircraft": n_aircraft,
        "crew": n_crew,
        "missions": len(scenario.missions),
        "relay_slots": n_relay_slots,
        "threats": len(scenario.threats),
        "airspaces": len(scenario.airspaces),
        "weather_cells": len(scenario.weather_cells),
        "store_lines": n_stores,
        "users": n_users,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the VAYU-COP exercise database.")
    parser.add_argument("--scenario", default="vayu_shield")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate all tables first")
    args = parser.parse_args()

    summary = run(scenario_name=args.scenario, do_reset=args.reset)

    print(f"Scenario: {args.scenario}")
    print("-" * 40)
    for key, value in summary.items():
        print(f"{key:>14}: {value}")


if __name__ == "__main__":
    main()
