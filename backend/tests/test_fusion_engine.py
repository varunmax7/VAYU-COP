from datetime import UTC, datetime, timedelta

import pytest
from app.core.db import SessionLocal
from app.models.aircraft import Aircraft
from app.models.threat import ThreatZone
from app.seed.generator import run as run_seed
from app.services.fusion.crosswalk import crosswalk, synthetic_icao24
from app.services.fusion.engine import fusion_engine
from app.services.fusion.types import (
    AircraftPositionRecord,
    AircraftStatusRecord,
    ThreatDetectionRecord,
)

NOW = datetime(2026, 11, 2, 13, 0, 0, tzinfo=UTC)


@pytest.fixture
def seeded_db():
    run_seed(scenario_name="vayu_shield", do_reset=True)
    db = SessionLocal()
    crosswalk.refresh(db)
    db.close()
    db = SessionLocal()
    yield db
    db.close()


def test_two_threat_sources_merge_into_one_zone_with_higher_confidence(seeded_db):
    existing = seeded_db.query(ThreatZone).filter_by(label="T-1").one()
    existing.last_seen = NOW
    existing.confidence = 0.0
    existing.sources = []
    seeded_db.commit()

    record_a = ThreatDetectionRecord(
        source="threat_intel_a",
        source_ts=NOW,
        label_hint="T-1",
        level="HIGH",
        lat=existing.center_lat + 0.01,
        lon=existing.center_lon + 0.01,
        confidence=0.85,
    )
    fusion_engine._apply_threat_detection(seeded_db, record_a, NOW)
    seeded_db.commit()
    seeded_db.refresh(existing)
    after_a = existing.confidence
    assert after_a == pytest.approx(0.85, abs=1e-6)

    record_b = ThreatDetectionRecord(
        source="threat_intel_b",
        source_ts=NOW + timedelta(seconds=30),
        label_hint="T-1",
        level="HIGH",
        lat=existing.center_lat - 0.005,
        lon=existing.center_lon - 0.005,
        confidence=0.80,
    )
    fusion_engine._apply_threat_detection(seeded_db, record_b, NOW + timedelta(seconds=30))
    seeded_db.commit()
    seeded_db.refresh(existing)

    # One zone, not two — and fused confidence beats either individual sensor's report.
    assert seeded_db.query(ThreatZone).filter_by(label="T-1").count() == 1
    assert existing.confidence > after_a
    assert existing.confidence > 0.80
    assert set(existing.sources) == {"threat_intel_a", "threat_intel_b"}


def test_track_feed_cannot_override_maint_mis_status(seeded_db):
    aircraft = seeded_db.query(Aircraft).filter_by(id="SU30-01").one()

    status_record = AircraftStatusRecord(
        source="maint_mis",
        source_ts=NOW,
        tail_number=aircraft.tail_number,
        status="UNSERVICEABLE",
    )
    fusion_engine._apply_aircraft_status(seeded_db, status_record, NOW)
    seeded_db.commit()
    seeded_db.refresh(aircraft)
    assert aircraft.status == "UNSERVICEABLE"
    assert aircraft.source == "maint_mis"

    # track_feed only ever carries position fields — it has no way to touch .status at
    # all, which is itself the authority enforcement (§8.2 step 4: "track feed can't
    # override maintenance status").
    position_record = AircraftPositionRecord(
        source="track_feed",
        source_ts=NOW + timedelta(seconds=1),
        icao24=synthetic_icao24(aircraft.id),
        lat=21.61,
        lon=78.21,
        alt_ft=0,
        heading_deg=90,
        speed_kts=0,
    )
    fusion_engine._apply_position(seeded_db, position_record, NOW + timedelta(seconds=1))
    seeded_db.commit()
    seeded_db.refresh(aircraft)

    assert aircraft.status == "UNSERVICEABLE"  # untouched by the position update
    assert aircraft.lat == 21.61 and aircraft.lon == 78.21
