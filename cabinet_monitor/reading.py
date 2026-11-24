"""The Reading type shared by all data sources, storage, alerts and charts."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Reading:
    """One temperature and humidity measurement at one place and time."""

    timestamp: datetime  # always timezone-aware UTC; convert only for display
    location: str
    temperature_c: float | None
    humidity_pct: float | None
