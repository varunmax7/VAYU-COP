"""Time and coordinate conversions the native source formats need (§8.1/8.2)."""

import re
from datetime import UTC, datetime, timedelta

IST_OFFSET = timedelta(hours=5, minutes=30)


def ensure_aware_utc(dt: datetime) -> datetime:
    """SQLite's DateTime(timezone=True) doesn't actually round-trip tzinfo — rows read
    back naive even though they were written aware. Treat a naive value as already UTC
    (everything in this app is written in UTC) so timestamp comparisons never raise."""
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


_DMS_RE = re.compile(
    r"""^\s*(?P<deg>\d+)[°:\s](?P<min>\d+)['′:\s](?P<sec>\d+(?:\.\d+)?)["″]?\s*(?P<hemi>[NSEW])\s*$""",
    re.VERBOSE,
)


def ist_to_utc(naive_ist: datetime) -> datetime:
    """Treat a naive datetime as IST wall-clock time and convert to UTC."""
    return (naive_ist - IST_OFFSET).replace(tzinfo=UTC)


def parse_ist_timestamp(text: str, fmt: str = "%d-%m-%Y %H:%M:%S") -> datetime:
    return ist_to_utc(datetime.strptime(text, fmt))


def decimal_to_dms(value: float, is_latitude: bool) -> str:
    hemi = ("N" if value >= 0 else "S") if is_latitude else ("E" if value >= 0 else "W")
    deg_digits = 2 if is_latitude else 3
    value = abs(value)
    deg = int(value)
    minutes_full = (value - deg) * 60
    minutes = int(minutes_full)
    seconds = round((minutes_full - minutes) * 60)
    return f"{deg:0{deg_digits}d}°{minutes:02d}'{seconds:02d}\"{hemi}"


def dms_to_decimal(dms: str) -> float:
    """ "24°24'00\"N" / "082°36'00\"E" -> signed decimal degrees."""
    match = _DMS_RE.match(dms.strip())
    if not match:
        raise ValueError(f"Not a recognisable DMS coordinate: {dms!r}")
    deg, minutes, sec = float(match["deg"]), float(match["min"]), float(match["sec"])
    value = deg + minutes / 60 + sec / 3600
    if match["hemi"] in ("S", "W"):
        value = -value
    return round(value, 6)
