"""Hourly observations from the FMI open data WFS API (timevaluepair format)."""

import math
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlencode, urlparse

from cabinet_monitor.reading import Reading

WFS_URL = "https://opendata.fmi.fi/wfs"
STORED_QUERY = "fmi::observations::weather::timevaluepair"
TIMEOUT_SECONDS = 30

_NS = {
    "omso": "http://inspire.ec.europa.eu/schemas/omso/3.0",
    "om": "http://www.opengis.net/om/2.0",
    "gml": "http://www.opengis.net/gml/3.2",
    "target": "http://xml.fmi.fi/namespace/om/atmosphericfeatures/1.1",
    "wml2": "http://www.opengis.net/waterml/2.0",
}
_XLINK_HREF = "{http://www.w3.org/1999/xlink}href"
_STATION_NAME = (
    "target:Location/gml:name"
    "[@codeSpace='http://xml.fmi.fi/namespace/locationcode/name']"
)
TEMPERATURE_PARAM = "t2m"
HUMIDITY_PARAM = "rh"


class FmiSource:
    """Reads the last N hours of observations from one FMI station."""

    def __init__(self, fmisid: int, hours: int) -> None:
        self.fmisid = fmisid
        self.hours = hours

    def read(self) -> list[Reading]:
        """Download and parse the latest hourly readings, oldest first."""
        start, end = time_window(datetime.now(timezone.utc), self.hours)
        url = build_query_url(self.fmisid, start, end)
        with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            return parse_fmi_xml(response.read())


def time_window(now: datetime, hours: int) -> tuple[datetime, datetime]:
    """Return (start, end) in UTC covering the last `hours` full hours."""
    if hours < 1:
        raise ValueError(f"hours must be at least 1, got {hours}")
    end = now.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(hours=hours - 1)
    return start, end


def build_query_url(fmisid: int, start: datetime, end: datetime) -> str:
    """Return the WFS URL for hourly temperature and humidity at a station."""
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "getFeature",
        "storedquery_id": STORED_QUERY,
        "fmisid": fmisid,
        "parameters": f"{TEMPERATURE_PARAM},{HUMIDITY_PARAM}",
        "timestep": 60,
        "starttime": _fmi_time(start),
        "endtime": _fmi_time(end),
    }
    return f"{WFS_URL}?{urlencode(params)}"


def _fmi_time(moment: datetime) -> str:
    """Format a datetime as FMI expects, e.g. '2026-11-24T08:00:00Z'."""
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_fmi_xml(xml_data: bytes) -> list[Reading]:
    """Turn an FMI timevaluepair response into readings, oldest first."""
    root = ET.fromstring(xml_data)
    observations = root.findall(".//omso:PointTimeSeriesObservation", _NS)
    if not observations:
        return []

    location = _station_name(root)
    series = {_parameter(obs): _time_series(obs) for obs in observations}
    temperatures = series.get(TEMPERATURE_PARAM, {})
    humidities = series.get(HUMIDITY_PARAM, {})

    times = sorted(temperatures.keys() | humidities.keys())
    return [
        Reading(t, location, temperatures.get(t), humidities.get(t))
        for t in times
    ]


def _station_name(root: ET.Element) -> str:
    """Return the station's human-readable name from the response."""
    name = root.find(f".//{_STATION_NAME}", _NS)
    if name is None or not name.text:
        raise ValueError("FMI response has no station name")
    return name.text.strip()


def _parameter(observation: ET.Element) -> str:
    """Return the parameter code (e.g. 't2m') an observation block holds."""
    prop = observation.find("om:observedProperty", _NS)
    href = prop.get(_XLINK_HREF, "") if prop is not None else ""
    return parse_qs(urlparse(href).query).get("param", [""])[0]


def _time_series(observation: ET.Element) -> dict[datetime, float | None]:
    """Return {UTC time: value} for one observation block; NaN becomes None."""
    series: dict[datetime, float | None] = {}
    for point in observation.iterfind(".//wml2:MeasurementTVP", _NS):
        time = datetime.fromisoformat(point.findtext("wml2:time", "", _NS))
        value = float(point.findtext("wml2:value", "nan", _NS))
        series[time] = None if math.isnan(value) else value
    return series
