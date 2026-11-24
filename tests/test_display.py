"""Tests for formatting readings as text in local time, using fake readings."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from cabinet_monitor.display import format_readings
from cabinet_monitor.reading import Reading

HELSINKI = ZoneInfo("Europe/Helsinki")


def reading(
    when: datetime, temp: float | None = 1.2, hum: float | None = 80.0
) -> Reading:
    """Return a fake reading at a given UTC time."""
    return Reading(when, "Test Station", temp, hum)


def lines(readings: list[Reading]) -> list[str]:
    """Format readings in Helsinki time and split into lines."""
    return format_readings(readings, HELSINKI).splitlines()


def test_header_shows_station_name_and_timezone() -> None:
    header = lines([reading(datetime(2026, 11, 24, 8, tzinfo=timezone.utc))])[0]
    assert header == "Test Station (times in Europe/Helsinki)"


def test_winter_time_is_utc_plus_2() -> None:
    row = lines([reading(datetime(2026, 11, 24, 8, tzinfo=timezone.utc))])[-1]
    assert row.startswith("2026-11-24 10:00 EET ")


def test_summer_time_is_utc_plus_3() -> None:
    row = lines([reading(datetime(2026, 7, 1, 12, tzinfo=timezone.utc))])[-1]
    assert row.startswith("2026-07-01 15:00 EEST")


def test_values_have_units() -> None:
    row = lines([reading(datetime(2026, 11, 24, 8, tzinfo=timezone.utc))])[-1]
    assert "1.2 °C" in row
    assert "80 %" in row


def test_negative_temperature() -> None:
    when = datetime(2026, 11, 24, 8, tzinfo=timezone.utc)
    row = lines([reading(when, temp=-12.3)])[-1]
    assert "-12.3 °C" in row


def test_missing_values_shown_as_dash() -> None:
    when = datetime(2026, 11, 24, 8, tzinfo=timezone.utc)
    row = lines([reading(when, temp=None, hum=None)])[-1]
    assert "°C" not in row
    assert "%" not in row
    assert row.count("–") == 2


def test_one_row_per_reading_in_given_order() -> None:
    readings = [
        reading(datetime(2026, 11, 24, hour, tzinfo=timezone.utc))
        for hour in (8, 9, 10)
    ]
    rows = lines(readings)[2:]
    assert [row[11:16] for row in rows] == ["10:00", "11:00", "12:00"]


def test_no_readings() -> None:
    assert format_readings([], HELSINKI) == "No readings received."
