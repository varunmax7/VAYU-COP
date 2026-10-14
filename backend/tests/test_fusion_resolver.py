from datetime import UTC, datetime, timedelta

import pytest
from app.services.fusion.resolver import (
    find_mergeable_threat,
    haversine_km,
    merge_confidence,
    merge_position,
    should_overwrite,
)

T0 = datetime(2026, 11, 2, 12, 0, 0, tzinfo=UTC)
T1 = T0 + timedelta(minutes=5)


def test_authoritative_source_wins_even_when_older():
    # track_feed is NOT authoritative for "status" — maint_mis is. A newer track_feed
    # record must never override an existing maint_mis-sourced status.
    overwrite = should_overwrite(
        "status",
        current_source="maint_mis",
        current_ts=T0,
        candidate_source="track_feed",
        candidate_ts=T1,  # newer, but not authoritative
    )
    assert overwrite is False


def test_same_authoritative_source_newest_wins():
    overwrite = should_overwrite(
        "status",
        current_source="maint_mis",
        current_ts=T0,
        candidate_source="maint_mis",
        candidate_ts=T1,
    )
    assert overwrite is True


def test_authoritative_source_overrides_non_authoritative_current():
    # Field "lat" is authoritative to track_feed; if the current value somehow came from
    # a non-authoritative source, the authoritative one takes over regardless of recency.
    overwrite = should_overwrite(
        "lat",
        current_source="maint_mis",
        current_ts=T1,
        candidate_source="track_feed",
        candidate_ts=T0,
    )
    assert overwrite is True


def test_field_with_no_authority_table_uses_recency():
    overwrite_newer = should_overwrite(
        "notes", current_source="a", current_ts=T0, candidate_source="b", candidate_ts=T1
    )
    overwrite_older = should_overwrite(
        "notes", current_source="a", current_ts=T1, candidate_source="b", candidate_ts=T0
    )
    assert overwrite_newer is True
    assert overwrite_older is False


def test_no_current_value_always_overwrites():
    assert should_overwrite(
        "status", current_source=None, current_ts=None, candidate_source="x", candidate_ts=T0
    )


def test_haversine_known_distance():
    # Alpha (21.60, 78.20) to Bravo (22.90, 80.60) is roughly 270 km.
    km = haversine_km(21.60, 78.20, 22.90, 80.60)
    assert 250 < km < 300


def test_merge_confidence_exceeds_either_input():
    merged = merge_confidence([0.85, 0.80])
    assert merged > 0.85
    assert merged > 0.80
    assert merged == pytest.approx(1 - (1 - 0.85) * (1 - 0.80), abs=1e-6)


def test_merge_position_is_weighted_mean():
    lat, lon = merge_position([(24.40, 82.60, 0.9), (24.42, 82.62, 0.1)])
    assert lat == pytest.approx(24.402, abs=1e-3)
    assert lon == pytest.approx(82.602, abs=1e-3)


class _FakeZone:
    def __init__(self, center_lat, center_lon, last_seen):
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.last_seen = last_seen


def test_find_mergeable_threat_within_radius_and_window():
    zone = _FakeZone(24.40, 82.60, T0)
    match = find_mergeable_threat([zone], 24.41, 82.61, T0 + timedelta(minutes=2))
    assert match is zone


def test_find_mergeable_threat_too_far_away():
    zone = _FakeZone(24.40, 82.60, T0)
    match = find_mergeable_threat([zone], 10.0, 70.0, T0 + timedelta(minutes=2))
    assert match is None


def test_find_mergeable_threat_outside_time_window():
    zone = _FakeZone(24.40, 82.60, T0)
    match = find_mergeable_threat([zone], 24.41, 82.61, T0 + timedelta(hours=2))
    assert match is None
