import random
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import AirBase
from app.models.weather import WeatherCell
from app.services.fusion.adapters.base import SourceAdapter
from app.services.fusion.resolver import haversine_km

BASE_STATION_CODES = {"ALPHA": "VABA", "BRAVO": "VABR", "CHARLIE": "VACH", "DELTA": "VADL"}
_NEARBY_CELL_KM = 100.0


class MetFeedAdapter(SourceAdapter):
    """Met Feed: METAR-like strings, e.g. "VABA 141300Z 22018G28KT 3000 TSRA BKN015CB"."""

    name = "met_feed"
    interval_s = 120.0

    def generate(self, db: Session, rng: random.Random, now: datetime) -> list[dict]:
        bases = list(db.scalars(select(AirBase)))
        cells = list(db.scalars(select(WeatherCell)))
        records = []

        for base in bases:
            station = BASE_STATION_CODES.get(base.code, base.code[:4].upper())
            nearby = [
                c
                for c in cells
                if haversine_km(base.lat, base.lon, c.center_lat, c.center_lon) <= _NEARBY_CELL_KM
            ]

            if nearby and nearby[0].severity == "severe":
                wind_dir, wind_kt, gust = (
                    rng.randint(180, 260),
                    rng.randint(15, 25),
                    rng.randint(25, 35),
                )
                visibility_m, weather, cloud = 3000, "TSRA", "BKN015CB"
            else:
                wind_dir, wind_kt, gust = rng.randint(0, 359), rng.randint(2, 12), 0
                visibility_m, weather, cloud = 9999, "", "FEW025"

            gust_group = f"G{gust:02d}" if gust else ""
            phenomena = f" {weather}" if weather else ""
            metar = (
                f"{station} {now.strftime('%d%H%M')}Z "
                f"{wind_dir:03d}{wind_kt:02d}{gust_group}KT {visibility_m}{phenomena} {cloud}"
            )
            records.append({"metar": metar})
        return records
