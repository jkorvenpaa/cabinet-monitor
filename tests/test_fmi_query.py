"""Tests for building the FMI query (time window and URL), no network."""

from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo

import pytest

from cabinet_monitor.sources.fmi import build_query_url, time_window


def test_time_window_ends_at_last_full_hour() -> None:
    now = datetime(2026, 11, 24, 10, 37, 12, tzinfo=timezone.utc)
    start, end = time_window(now, hours=4)
    assert start == datetime(2026, 11, 24, 7, tzinfo=timezone.utc)
    assert end == datetime(2026, 11, 24, 10, tzinfo=timezone.utc)


def test_time_window_is_utc_even_if_now_is_helsinki_time() -> None:
    now = datetime(2026, 11, 24, 12, 37, tzinfo=ZoneInfo("Europe/Helsinki"))
    start, end = time_window(now, hours=1)
    assert start == end == datetime(2026, 11, 24, 10, tzinfo=timezone.utc)
    assert end.tzinfo == timezone.utc


def test_time_window_rejects_zero_hours() -> None:
    now = datetime(2026, 11, 24, 10, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        time_window(now, hours=0)


def test_query_url_asks_for_hourly_t2m_and_rh_at_station() -> None:
    start = datetime(2026, 11, 24, 7, tzinfo=timezone.utc)
    end = datetime(2026, 11, 24, 10, tzinfo=timezone.utc)
    url = build_query_url(101004, start, end)

    parsed = urlparse(url)
    query = {key: values[0] for key, values in parse_qs(parsed.query).items()}
    assert parsed.scheme == "https"
    assert parsed.netloc == "opendata.fmi.fi"
    assert query == {
        "service": "WFS",
        "version": "2.0.0",
        "request": "getFeature",
        "storedquery_id": "fmi::observations::weather::timevaluepair",
        "fmisid": "101004",
        "parameters": "t2m,rh",
        "timestep": "60",
        "starttime": "2026-11-24T07:00:00Z",
        "endtime": "2026-11-24T10:00:00Z",
    }
