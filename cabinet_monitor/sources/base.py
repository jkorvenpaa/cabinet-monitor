"""The interface every data source (FMI, a real sensor, ...) implements."""

from typing import Protocol

from cabinet_monitor.reading import Reading


class Source(Protocol):
    """Anything that can produce readings."""

    def read(self) -> list[Reading]:
        """Return the latest readings, oldest first, timestamps in UTC."""
        ...
