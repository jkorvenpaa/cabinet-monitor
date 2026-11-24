"""Tests for parsing FMI timevaluepair XML into readings (no network)."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from cabinet_monitor.sources.fmi import parse_fmi_xml

FIXTURES = Path(__file__).parent / "fixtures"


def utc(hour: int) -> datetime:
    """Return 2026-11-24 at the given hour, UTC."""
    return datetime(2026, 11, 24, hour, tzinfo=timezone.utc)


def load(name: str) -> bytes:
    """Return the raw bytes of a fixture file."""
    return (FIXTURES / name).read_bytes()


def test_location_is_station_name_from_response() -> None:
    readings = parse_fmi_xml(load("fmi_kumpula.xml"))
    assert {r.location for r in readings} == {"Helsinki Kumpula"}


def test_one_reading_per_hour_oldest_first() -> None:
    readings = parse_fmi_xml(load("fmi_kumpula.xml"))
    assert [r.timestamp for r in readings] == [utc(8), utc(9), utc(10), utc(11)]


def test_timestamps_are_aware_utc() -> None:
    readings = parse_fmi_xml(load("fmi_kumpula.xml"))
    assert all(r.timestamp.utcoffset() == timedelta(0) for r in readings)


def test_temperature_and_humidity_paired_by_time() -> None:
    readings = parse_fmi_xml(load("fmi_kumpula.xml"))
    pairs = [(r.temperature_c, r.humidity_pct) for r in readings]
    assert pairs == [(1.2, 80.0), (1.3, 80.0), (1.3, 80.0), (1.3, 79.0)]


def test_nan_becomes_none() -> None:
    readings = parse_fmi_xml(load("fmi_kumpula_nan.xml"))
    by_hour = {r.timestamp.hour: r for r in readings}
    assert by_hour[9].temperature_c is None
    assert by_hour[9].humidity_pct == 80.0
    assert by_hour[11].humidity_pct is None
    assert by_hour[11].temperature_c == 1.3


def test_response_without_observations_gives_empty_list() -> None:
    empty = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0"'
        b' numberMatched="0" numberReturned="0"/>'
    )
    assert parse_fmi_xml(empty) == []
