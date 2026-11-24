"""Format readings as plain text, converting UTC timestamps to local time."""

from zoneinfo import ZoneInfo

from cabinet_monitor.reading import Reading

MISSING = "–"


def format_readings(readings: list[Reading], tz: ZoneInfo) -> str:
    """Return a header line plus one line per reading, times shown in `tz`."""
    if not readings:
        return "No readings received."
    header = f"{readings[0].location} (times in {tz.key})"
    rows = [_format_row(r, tz) for r in readings]
    return "\n".join([header, "", *rows])


def _format_row(reading: Reading, tz: ZoneInfo) -> str:
    """Return one aligned line: local time, temperature, humidity."""
    local = reading.timestamp.astimezone(tz)
    time = f"{local:%Y-%m-%d %H:%M} {local:%Z}"
    temp = MISSING if reading.temperature_c is None else f"{reading.temperature_c:.1f} °C"
    hum = MISSING if reading.humidity_pct is None else f"{reading.humidity_pct:.0f} %"
    return f"{time:<21}{temp:>9}{hum:>7}"
