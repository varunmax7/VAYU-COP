from datetime import date

import pytest
from app.services.fusion.normaliser import parse_metar, parse_notam
from app.services.fusion.time_utils import decimal_to_dms, dms_to_decimal


def test_parse_metar_wind_visibility_ceiling_thunderstorm():
    obs = parse_metar("VABA 141300Z 22018G28KT 3000 TSRA BKN015CB", date(2026, 11, 14))
    assert obs.base_id == "VABA"
    assert obs.wind_kt == 18.0
    assert obs.gust_kt == 28.0
    assert obs.visibility_km == 3.0
    assert obs.ceiling_ft == 1500.0  # BKN015 -> 1500 ft
    assert obs.thunderstorm is True
    assert obs.valid_ts.day == 14
    assert obs.valid_ts.hour == 13
    assert obs.valid_ts.minute == 0


def test_parse_metar_benign_weather_no_ceiling_layer():
    obs = parse_metar("VABR 020600Z 04508KT 9999 FEW250", date(2026, 11, 2))
    assert obs.thunderstorm is False
    assert obs.gust_kt == 0.0
    assert obs.visibility_km == 10.0
    assert obs.ceiling_ft == 12000.0  # no BKN/OVC layer -> "unlimited" default


def test_parse_metar_rejects_garbage():
    with pytest.raises(ValueError):
        parse_metar("NOT A METAR", date(2026, 11, 2))


def test_parse_notam_with_time_window():
    window = parse_notam("AIRSPACE OSCAR CLOSED 1315Z-1800Z", date(2026, 11, 2))
    assert window.airspace_id == "OSCAR"
    assert window.status == "CLOSED"
    assert window.active_from.hour == 13
    assert window.active_from.minute == 15
    assert window.active_to.hour == 18
    assert window.active_to.minute == 0


def test_parse_notam_without_time_window():
    window = parse_notam("AIRSPACE ROMEO OPEN", date(2026, 11, 2))
    assert window.airspace_id == "ROMEO"
    assert window.status == "OPEN"
    assert window.active_from is None
    assert window.active_to is None


def test_parse_notam_rejects_garbage():
    with pytest.raises(ValueError):
        parse_notam("CLOSE THE AIRSPACE PLEASE", date(2026, 11, 2))


@pytest.mark.parametrize(
    ("dms", "expected"),
    [
        ("24°24'00\"N", 24.4),
        ("082°36'00\"E", 82.6),
        ("18°30'00\"S", -18.5),
    ],
)
def test_dms_to_decimal(dms: str, expected: float):
    assert dms_to_decimal(dms) == pytest.approx(expected, abs=1e-4)


def test_decimal_to_dms_round_trips():
    for lat, lon in [(24.4, 82.6), (17.5, 74.0), (25.5, 84.0)]:
        lat_dms = decimal_to_dms(lat, is_latitude=True)
        lon_dms = decimal_to_dms(lon, is_latitude=False)
        assert dms_to_decimal(lat_dms) == pytest.approx(lat, abs=1 / 3600)
        assert dms_to_decimal(lon_dms) == pytest.approx(lon, abs=1 / 3600)
