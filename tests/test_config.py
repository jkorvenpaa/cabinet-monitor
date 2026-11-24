"""Tests for loading config.toml, using temporary files."""

from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from cabinet_monitor.config import Config, ConfigError, load_config

VALID = """
[fmi]
fmisid = 101004
hours = 24

[display]
timezone = "Europe/Helsinki"
"""


def write(tmp_path: Path, text: str) -> Path:
    """Write text to a config file in a temporary directory, return its path."""
    path = tmp_path / "config.toml"
    path.write_text(text)
    return path


def test_valid_config_is_loaded(tmp_path: Path) -> None:
    config = load_config(write(tmp_path, VALID))
    assert config == Config(
        fmisid=101004, hours=24, timezone=ZoneInfo("Europe/Helsinki")
    )


def test_missing_key_names_the_key(tmp_path: Path) -> None:
    path = write(tmp_path, VALID.replace("hours = 24", ""))
    with pytest.raises(ConfigError, match="fmi.hours"):
        load_config(path)


def test_missing_section_names_the_key(tmp_path: Path) -> None:
    path = write(tmp_path, VALID.split("[display]")[0])
    with pytest.raises(ConfigError, match="display.timezone"):
        load_config(path)


def test_wrong_type_is_rejected(tmp_path: Path) -> None:
    path = write(tmp_path, VALID.replace("101004", '"Kumpula"'))
    with pytest.raises(ConfigError, match="fmi.fmisid"):
        load_config(path)


def test_boolean_is_not_accepted_as_number(tmp_path: Path) -> None:
    path = write(tmp_path, VALID.replace("hours = 24", "hours = true"))
    with pytest.raises(ConfigError, match="fmi.hours"):
        load_config(path)


def test_hours_must_be_positive(tmp_path: Path) -> None:
    path = write(tmp_path, VALID.replace("hours = 24", "hours = 0"))
    with pytest.raises(ConfigError, match="fmi.hours"):
        load_config(path)


def test_unknown_timezone_is_rejected(tmp_path: Path) -> None:
    path = write(tmp_path, VALID.replace("Europe/Helsinki", "Europe/Kumpula"))
    with pytest.raises(ConfigError, match="Europe/Kumpula"):
        load_config(path)


def test_invalid_toml_is_reported(tmp_path: Path) -> None:
    path = write(tmp_path, "[fmi\nfmisid = ")
    with pytest.raises(ConfigError):
        load_config(path)
