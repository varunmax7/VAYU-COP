"""Open-Meteo hourly forecast client with a synthetic fallback (§11, WEATHER_MODE)."""

import logging
import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import httpx

logger = logging.getLogger("vayu.fusion.weather")

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT_S = 5.0
HOURLY_FIELDS = "visibility,cloud_cover_low,wind_speed_10m,wind_gusts_10m,precipitation,cape"


@dataclass(frozen=True)
class ForecastHour:
    valid_ts: datetime
    ceiling_ft: float
    visibility_km: float
    wind_kt: float
    gust_kt: float
    precip_mm: float
    thunderstorm: bool


async def fetch_open_meteo(lat: float, lon: float, hours: int = 24) -> list[ForecastHour] | None:
    """Returns None (never raises) on any network/parse failure, so callers can fall back."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": HOURLY_FIELDS,
        "forecast_days": 2,
        "timezone": "UTC",
    }
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
            response = await client.get(OPEN_METEO_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning(f"Open-Meteo fetch failed, falling back to synthetic: {exc}")
        return None

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    if not times:
        return None

    results = []
    for i, t in enumerate(times[:hours]):
        cloud_cover_low = hourly.get("cloud_cover_low", [0] * len(times))[i]
        wind_kt = hourly.get("wind_speed_10m", [0] * len(times))[i] * 0.539957  # km/h -> kt
        gust_kt = hourly.get("wind_gusts_10m", [0] * len(times))[i] * 0.539957
        precip_mm = hourly.get("precipitation", [0] * len(times))[i]
        cape = hourly.get("cape", [0] * len(times))[i]
        visibility_m = hourly.get("visibility", [10000] * len(times))[i]
        results.append(
            ForecastHour(
                valid_ts=datetime.fromisoformat(t).replace(tzinfo=UTC),
                ceiling_ft=12000.0 if cloud_cover_low < 50 else 1500.0,
                visibility_km=(visibility_m or 10000) / 1000,
                wind_kt=round(wind_kt, 1),
                gust_kt=round(gust_kt, 1),
                precip_mm=precip_mm or 0.0,
                thunderstorm=bool(cape and cape > 1000),
            )
        )
    return results


def synthetic_forecast(rng: random.Random, now: datetime, hours: int = 24) -> list[ForecastHour]:
    results = []
    for i in range(hours):
        thunderstorm = rng.random() < 0.08
        results.append(
            ForecastHour(
                valid_ts=now + timedelta(hours=i),
                ceiling_ft=1500.0 if thunderstorm else rng.uniform(5000, 12000),
                visibility_km=3.0 if thunderstorm else rng.uniform(6, 10),
                wind_kt=rng.uniform(15, 30) if thunderstorm else rng.uniform(3, 15),
                gust_kt=rng.uniform(25, 40) if thunderstorm else 0.0,
                precip_mm=rng.uniform(1, 5) if thunderstorm else 0.0,
                thunderstorm=thunderstorm,
            )
        )
    return results


async def get_forecast(
    lat: float, lon: float, *, mode: str, rng: random.Random, now: datetime, hours: int = 24
) -> list[ForecastHour]:
    if mode == "synthetic":
        return synthetic_forecast(rng, now, hours)

    live = await fetch_open_meteo(lat, lon, hours)
    if live is not None:
        return live

    if mode == "live":
        logger.warning("WEATHER_MODE=live but Open-Meteo is unreachable; using synthetic data")
    return synthetic_forecast(rng, now, hours)
