"""Entry point: `python -m cabinet_monitor` fetches and prints readings."""

import sys
from pathlib import Path
from xml.etree.ElementTree import ParseError

from cabinet_monitor.config import ConfigError, load_config
from cabinet_monitor.display import format_readings
from cabinet_monitor.sources.fmi import FmiSource

CONFIG_PATH = Path("config.toml")


def main() -> int:
    """Load config, read from the source, print the result; return exit code."""
    try:
        config = load_config(CONFIG_PATH)
        source = FmiSource(config.fmisid, config.hours)
        readings = source.read()
    except ConfigError as error:
        print(f"Config error: {error}", file=sys.stderr)
        return 1
    except (OSError, ParseError, ValueError) as error:
        print(f"Could not read data: {error}", file=sys.stderr)
        return 1
    print(format_readings(readings, config.timezone))
    return 0


if __name__ == "__main__":
    sys.exit(main())
