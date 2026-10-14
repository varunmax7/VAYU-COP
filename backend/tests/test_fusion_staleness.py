from datetime import UTC, datetime, timedelta

import pytest
from app.core.db import SessionLocal
from app.models.threat import ThreatZone
from app.seed.generator import run as run_seed
from app.services.fusion.staleness import STALE_MAX_AGE_S, sweep_staleness

NOW = datetime(2026, 11, 2, 13, 0, 0, tzinfo=UTC)


@pytest.fixture
def seeded_db():
    run_seed(scenario_name="vayu_shield", do_reset=True)
    db = SessionLocal()
    yield db
    db.close()


def test_fresh_entity_is_not_marked_stale(seeded_db):
    zone = seeded_db.query(ThreatZone).first()
    zone.fused_ts = NOW
    zone.stale = False
    seeded_db.commit()

    transitions = sweep_staleness(seeded_db, now=NOW + timedelta(seconds=5))
    seeded_db.commit()

    seeded_db.refresh(zone)
    assert zone.stale is False
    assert not any(t.entity_id == zone.id for t in transitions)


def test_entity_past_max_age_is_marked_stale(seeded_db):
    zone = seeded_db.query(ThreatZone).first()
    max_age = STALE_MAX_AGE_S["threat"]
    zone.fused_ts = NOW
    zone.stale = False
    seeded_db.commit()

    transitions = sweep_staleness(seeded_db, now=NOW + timedelta(seconds=max_age + 1))
    seeded_db.commit()

    seeded_db.refresh(zone)
    assert zone.stale is True
    assert any(t.entity_id == zone.id and t.entity_kind == "ThreatZone" for t in transitions)


def test_already_stale_entity_does_not_reappear_in_transitions(seeded_db):
    zone = seeded_db.query(ThreatZone).first()
    max_age = STALE_MAX_AGE_S["threat"]
    zone.fused_ts = NOW
    zone.stale = True  # already flagged stale from a previous sweep
    seeded_db.commit()

    transitions = sweep_staleness(seeded_db, now=NOW + timedelta(seconds=max_age + 1))

    assert not any(t.entity_id == zone.id for t in transitions)


def test_disabling_a_threat_source_eventually_produces_staleness(seeded_db):
    """Models the acceptance scenario: once a source stops refreshing an entity, that
    entity's fused_ts falls behind and the sweep marks it stale after its max age — the
    same mechanism a live `PATCH /fusion/sources/threat_intel_b {"enabled": false}`
    relies on, without needing to wait out the real 20-minute window in a test."""
    zone = seeded_db.query(ThreatZone).first()
    zone.fused_ts = NOW
    zone.stale = False
    seeded_db.commit()

    just_before = sweep_staleness(
        seeded_db, now=NOW + timedelta(seconds=STALE_MAX_AGE_S["threat"] - 1)
    )
    seeded_db.commit()
    seeded_db.refresh(zone)
    assert zone.stale is False
    assert not any(t.entity_id == zone.id for t in just_before)

    after = sweep_staleness(seeded_db, now=NOW + timedelta(seconds=STALE_MAX_AGE_S["threat"] + 1))
    seeded_db.commit()
    seeded_db.refresh(zone)
    assert zone.stale is True
    assert any(t.entity_id == zone.id for t in after)
