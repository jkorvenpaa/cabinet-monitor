# cabinet-monitor

A small Python tool for watching the climate in a plant cabinet (aroids,
target ~70–80 % relative humidity). It collects temperature and humidity
readings over time, stores them, charts them, and alerts when something
looks wrong.

## Status

Early development: the project structure and goals are set, and the
code is not written yet. Nothing here is usable yet.

## Plan

- **Data source** – until the sensor hardware is connected, hourly
  readings come from the Finnish Meteorological Institute (FMI) open data
  API. Each source implements the same small interface, so the
  sensor can replace FMI without changes elsewhere.
- **Storage** – readings saved in SQLite.
- **Analysis and alerts** – flags readings outside the configured
  thresholds. It does not depend on the data source or the database.
- **Charts** – temperature and humidity over time.
- **Configuration** – station, thresholds and intervals in a config file.

## Tech

Python 3.13 with the standard library where possible, and pytest for tests.
