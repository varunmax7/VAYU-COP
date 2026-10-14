"""Parses each adapter's native raw format into a canonical NormalizedRecord (§8.2 step 1)."""

import re
from datetime import UTC, date, datetime, timedelta

from app.services.fusion.time_utils import dms_to_decimal, ist_to_utc
from app.services.fusion.types import (
    AircraftPositionRecord,
    AircraftStatusRecord,
    AirspaceWindowRecord,
    CrewStatusRecord,
    MissionRequestRecord,
    StoreDeltaRecord,
    ThreatDetectionRecord,
    WeatherObsRecord,
)

MAINT_STATUS_CODES = {
    "RDY": "READY",
    "USV": "UNSERVICEABLE",
    "MNT": "MAINTENANCE",
    "TRN": "TURNAROUND",
    "TSK": "TASKED",
    "ABN": "AIRBORNE",
}

CREW_STATUS_CODES = {
    "AVL": "AVAILABLE",
    "ODY": "ON_DUTY",
    "ABN": "AIRBORNE",
    "RST": "RESTING",
    "LV": "LEAVE",
    "MED": "MEDICAL",
}

STORE_CODE_MAP = {
    "S-AD1": "AD_STD",
    "S-RC1": "RECCE_POD",
    "S-GA1": "GA_GENERIC",
    "S-CP1": "CARGO_PALLET",
    "S-TK1": "TANKER_PODS",
    "S-AW1": "AEW_NIL",
    "S-SR1": "SAR_KIT",
    "S-HD1": "HADR_KIT",
}

_WIND_RE = re.compile(r"^(?P<dir>\d{3}|VRB)(?P<spd>\d{2,3})(G(?P<gust>\d{2,3}))?KT$")
_CLOUD_RE = re.compile(r"^(?P<cover>FEW|SCT|BKN|OVC)(?P<height>\d{3})(CB|TCU)?$")
_TIME_GROUP_RE = re.compile(r"^(?P<day>\d{2})(?P<hour>\d{2})(?P<minute>\d{2})Z$")


def parse_maint_mis(raw: dict, source: str = "maint_mis") -> AircraftStatusRecord:
    return AircraftStatusRecord(
        source=source,
        source_ts=ist_to_utc(datetime.strptime(raw["ts_ist"], "%d-%m-%Y %H:%M:%S")),
        tail_number=raw["tail"],
        status=MAINT_STATUS_CODES.get(raw["status_code"], raw["status_code"]),
        hours_since_maint=raw.get("hours_since_maint"),
        hours_to_next_maint=raw.get("hours_to_next_maint"),
        snag=raw.get("snag"),
    )


def parse_crew_roster(raw: dict, source: str = "crew_roster") -> CrewStatusRecord:
    duty_start = None
    if raw.get("duty_start_ist"):
        duty_start = ist_to_utc(datetime.strptime(raw["duty_start_ist"], "%d-%m-%Y %H:%M:%S"))
    return CrewStatusRecord(
        source=source,
        source_ts=ist_to_utc(datetime.strptime(raw["ts_ist"], "%d-%m-%Y %H:%M:%S")),
        service_number=raw["svc_no"],
        status=CREW_STATUS_CODES.get(raw["status_code"], raw["status_code"]),
        duty_start=duty_start,
        duty_hours_24h=raw.get("duty_hours_24h"),
        rest_ok=raw.get("rest_ok", "Y") == "Y",
    )


def parse_stores_inv(raw: dict, source: str = "stores_inv") -> StoreDeltaRecord:
    return StoreDeltaRecord(
        source=source,
        source_ts=datetime.fromisoformat(raw["ts_utc"]),
        base_id=raw["base"],
        category=STORE_CODE_MAP.get(raw["code"], raw["code"]),
        available=raw["qty_avail"],
        reserved=raw.get("qty_resv", 0),
    )


def parse_metar(metar: str, reference_date: date, source: str = "met_feed") -> WeatherObsRecord:
    """ "VABA 141300Z 22018G28KT 3000 TSRA BKN015CB" -> a canonical observation.
    The day-of-month in the time group is anchored to `reference_date`'s year/month.
    """
    tokens = metar.strip().split()
    station = tokens[0]

    time_match = _TIME_GROUP_RE.match(tokens[1])
    if not time_match:
        raise ValueError(f"Not a recognisable METAR time group: {tokens[1]!r}")
    valid_ts = datetime(
        reference_date.year,
        reference_date.month,
        int(time_match["day"]),
        int(time_match["hour"]),
        int(time_match["minute"]),
        tzinfo=UTC,
    )

    wind_match = _WIND_RE.match(tokens[2])
    if not wind_match:
        raise ValueError(f"Not a recognisable METAR wind group: {tokens[2]!r}")
    wind_kt = float(wind_match["spd"])
    gust_kt = float(wind_match["gust"]) if wind_match["gust"] else 0.0

    vis_token = tokens[3]
    visibility_km = 10.0 if vis_token in ("9999", "CAVOK") else float(vis_token) / 1000

    thunderstorm = False
    ceiling_ft = 12000.0  # "unlimited" ceiling when no BKN/OVC layer is reported
    for token in tokens[4:]:
        cloud_match = _CLOUD_RE.match(token)
        if cloud_match:
            if cloud_match["cover"] in ("BKN", "OVC"):
                layer_ft = float(cloud_match["height"]) * 100
                ceiling_ft = min(ceiling_ft, layer_ft)
            continue
        if "TS" in token:
            thunderstorm = True

    precip_mm = 2.0 if thunderstorm or any("RA" in t for t in tokens[4:]) else 0.0

    return WeatherObsRecord(
        source=source,
        source_ts=valid_ts,
        base_id=station,
        valid_ts=valid_ts,
        ceiling_ft=ceiling_ft,
        visibility_km=visibility_km,
        wind_kt=wind_kt,
        gust_kt=gust_kt,
        precip_mm=precip_mm,
        thunderstorm=thunderstorm,
        is_forecast=False,
    )


def parse_notam(
    notam: str, reference_date: date, source: str = "airspace_notam"
) -> AirspaceWindowRecord:
    """ "AIRSPACE OSCAR CLOSED 1315Z-1800Z" -> a canonical airspace status window.
    A trailing "HHMMZ-HHMMZ" window is optional; without one the status is unbounded.
    """
    tokens = notam.strip().split()
    if len(tokens) < 3 or tokens[0] != "AIRSPACE":
        raise ValueError(f"Not a recognisable NOTAM: {notam!r}")

    airspace_id = tokens[1]
    status = tokens[2]
    active_from = active_to = None

    if len(tokens) >= 4:
        window_match = re.match(r"^(\d{4})Z-(\d{4})Z$", tokens[3])
        if not window_match:
            raise ValueError(f"Not a recognisable NOTAM time window: {tokens[3]!r}")
        start_h, start_m = int(window_match[1][:2]), int(window_match[1][2:])
        end_h, end_m = int(window_match[2][:2]), int(window_match[2][2:])
        active_from = datetime(
            reference_date.year,
            reference_date.month,
            reference_date.day,
            start_h,
            start_m,
            tzinfo=UTC,
        )
        active_to = datetime(
            reference_date.year,
            reference_date.month,
            reference_date.day,
            end_h,
            end_m,
            tzinfo=UTC,
        )
        if active_to <= active_from:
            active_to += timedelta(days=1)

    return AirspaceWindowRecord(
        source=source,
        source_ts=active_from or datetime.now(UTC),
        airspace_id=airspace_id,
        status=status,
        active_from=active_from,
        active_to=active_to,
    )


def parse_threat_intel_a(raw: dict, source: str = "threat_intel_a") -> ThreatDetectionRecord:
    """Decimal coordinates, confidence already on a 0-1 scale."""
    return ThreatDetectionRecord(
        source=source,
        source_ts=datetime.fromisoformat(raw["ts_utc"]),
        label_hint=raw["id_hint"],
        level=raw["level"],
        lat=raw["lat"],
        lon=raw["lon"],
        confidence=raw["conf"],
    )


def parse_threat_intel_b(raw: dict, source: str = "threat_intel_b") -> ThreatDetectionRecord:
    """DMS coordinates, confidence on a 1-5 scale -> normalised to 0-1."""
    return ThreatDetectionRecord(
        source=source,
        source_ts=datetime.fromisoformat(raw["ts_utc"]),
        label_hint=raw["id_hint"],
        level=raw["level"],
        lat=dms_to_decimal(raw["lat_dms"]),
        lon=dms_to_decimal(raw["lon_dms"]),
        confidence=raw["conf_5"] / 5.0,
    )


def parse_track_feed(raw: dict, source: str = "track_feed") -> AircraftPositionRecord:
    return AircraftPositionRecord(
        source=source,
        source_ts=datetime.fromisoformat(raw["ts_utc"]),
        icao24=raw["icao24"],
        lat=raw["lat"],
        lon=raw["lon"],
        alt_ft=raw["alt_ft"],
        heading_deg=raw["trk_deg"],
        speed_kts=raw["gs_kt"],
    )


def parse_tasking(raw: dict, source: str = "tasking") -> MissionRequestRecord:
    return MissionRequestRecord(
        source=source,
        source_ts=datetime.fromisoformat(raw["ts_utc"]),
        code=raw["code"],
        type=raw["type"],
        priority=raw["priority"],
        area_name=raw["area_name"],
        center_lat=raw["lat"],
        center_lon=raw["lon"],
        earliest_start=datetime.fromisoformat(raw["earliest_start"]),
        latest_start=datetime.fromisoformat(raw["latest_start"]),
        on_station_min=raw["on_station_min"],
        required_aircraft=raw.get("required_aircraft", 1),
        required_store=raw.get("required_store"),
    )
