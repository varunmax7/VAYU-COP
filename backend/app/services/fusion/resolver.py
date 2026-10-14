"""Conflict resolution (§8.2 step 4) and entity resolution for threats (§8.2 step 3)."""

import math
from datetime import datetime

from app.models.threat import ThreatZone
from app.services.fusion.time_utils import ensure_aware_utc

# Field-level source authority: for a given field, the listed sources are authoritative,
# highest-priority first. A non-listed source can only ever lose to an authoritative one,
# regardless of timestamp. Recency only breaks ties *within* the authoritative source,
# or decides when no source in the list matches (open fields fall back to "newest wins").
FIELD_AUTHORITY: dict[str, list[str]] = {
    "status": ["maint_mis"],  # Aircraft.status
    "lat": ["track_feed"],
    "lon": ["track_feed"],
    "heading_deg": ["track_feed"],
    "alt_ft": ["track_feed"],
    "speed_kts": ["track_feed"],
    "fuel_pct": ["track_feed", "maint_mis"],
    "hours_since_maint": ["maint_mis"],
    "hours_to_next_maint": ["maint_mis"],
}

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def should_overwrite(
    field_name: str,
    *,
    current_source: str | None,
    current_ts: datetime | None,
    candidate_source: str,
    candidate_ts: datetime,
) -> bool:
    """True if `candidate` should replace the field's current value."""
    if current_source is None or current_ts is None:
        return True
    current_ts = ensure_aware_utc(current_ts)
    candidate_ts = ensure_aware_utc(candidate_ts)

    authority = FIELD_AUTHORITY.get(field_name)
    if not authority:
        # No designated authority for this field: newest timestamp wins outright.
        return candidate_ts >= current_ts

    current_rank = (
        authority.index(current_source) if current_source in authority else len(authority)
    )
    candidate_rank = (
        authority.index(candidate_source) if candidate_source in authority else len(authority)
    )

    if candidate_rank < current_rank:
        return True
    if candidate_rank > current_rank:
        return False
    # Same authority rank (including "neither is authoritative"): newest wins.
    return candidate_ts >= current_ts


# Threats within this distance and time window are treated as the same physical entity.
THREAT_MERGE_RADIUS_KM = 25.0
THREAT_MERGE_WINDOW_S = 600  # 10 minutes


def find_mergeable_threat(
    existing: list[ThreatZone], lat: float, lon: float, detected_ts: datetime
) -> ThreatZone | None:
    detected_ts = ensure_aware_utc(detected_ts)
    for zone in existing:
        within_distance = (
            haversine_km(zone.center_lat, zone.center_lon, lat, lon) <= THREAT_MERGE_RADIUS_KM
        )
        last_seen = ensure_aware_utc(zone.last_seen)
        within_time = abs((last_seen - detected_ts).total_seconds()) <= THREAT_MERGE_WINDOW_S
        if within_distance and within_time:
            return zone
    return None


def merge_confidence(confidences: list[float]) -> float:
    """confidence = 1 - prod(1 - c_i), per §8.2 step 3."""
    product = 1.0
    for c in confidences:
        product *= 1 - max(0.0, min(1.0, c))
    return round(1 - product, 4)


def merge_position(
    positions: list[tuple[float, float, float]],
) -> tuple[float, float]:
    """Confidence-weighted mean of [(lat, lon, confidence), ...]."""
    total_weight = sum(w for _, _, w in positions) or 1.0
    lat = sum(lat * w for lat, _, w in positions) / total_weight
    lon = sum(lon * w for _, lon, w in positions) / total_weight
    return round(lat, 6), round(lon, 6)
