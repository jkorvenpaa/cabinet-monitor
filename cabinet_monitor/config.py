"""Load settings from config.toml into a validated Config object."""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class ConfigError(ValueError):
    """Raised when the config file is missing, malformed or has bad values."""


@dataclass(frozen=True)
class Config:
    """All settings the program needs."""

    fmisid: int
    hours: int
    timezone: ZoneInfo


def load_config(path: Path) -> Config:
    """Read and validate the config file at `path`."""
    data = _read_toml(path)
    hours = _get(data, "fmi", "hours", int)
    if hours < 1:
        raise ConfigError(f"fmi.hours must be at least 1, got {hours}")
    return Config(
        fmisid=_get(data, "fmi", "fmisid", int),
        hours=hours,
        timezone=_timezone(_get(data, "display", "timezone", str)),
    )


def _read_toml(path: Path) -> dict[str, Any]:
    """Parse the TOML file, turning file and syntax errors into ConfigError."""
    try:
        with path.open("rb") as file:
            return tomllib.load(file)
    except OSError as error:
        raise ConfigError(f"cannot read {path}: {error}") from error
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"invalid TOML in {path}: {error}") from error


def _get[T](data: dict[str, Any], section: str, key: str, kind: type[T]) -> T:
    """Return data[section][key], checking that it exists and has type `kind`."""
    name = f"{section}.{key}"
    table = data.get(section, {})
    value = table.get(key) if isinstance(table, dict) else None
    if value is None:
        raise ConfigError(f"missing setting {name}")
    # bool is a subclass of int in Python, so `true` would pass as 1 otherwise.
    if isinstance(value, bool) or not isinstance(value, kind):
        raise ConfigError(f"{name} must be {kind.__name__}, got {value!r}")
    return value


def _timezone(name: str) -> ZoneInfo:
    """Return the ZoneInfo for an IANA name like 'Europe/Helsinki'."""
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as error:
        raise ConfigError(f"unknown timezone {name!r}") from error
