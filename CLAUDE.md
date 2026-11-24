# Project: cabinet-monitor

A small Python tool that collects temperature and humidity readings over time,
stores them, charts them, and alerts when something looks wrong.
It was designed for my plant cabinet (aroids, ~70–80 % humidity). Until the
sensor hardware is connected, it reads hourly data from the Finnish
Meteorological Institute (FMI) open data API.

## About me and how I want to work

- I know C and C++ well (from my software studies) and I'm new to Python.
  Point out Python idioms and pitfalls that differ from C/C++ when they come up.
- I want to stay in control and understand every change. You do the legwork;
  I make the decisions.
- Before writing any code for a new feature, propose a short plan and wait
  for my approval.
- Work in small steps. One feature or fix at a time.
- After each change, explain in a few sentences what you changed and why.
- If you are unsure about something (an API, a library version, a formula),
  say so instead of guessing. Point me to where I can check it.
- Never commit, push, or delete files. I do all Git operations myself.
- Don't add new dependencies without asking me first.

## Architecture rules

- The data source must be swappable. All sources (FMI now, a real sensor
  later) implement the same small interface, e.g. `read() -> list[Reading]`.
  Nothing outside the source module should know where data comes from.
- Keep the layers separate: data source, storage (SQLite), analysis/alerts,
  charts. Alert logic must not depend on FMI or on the database.
- Configuration (station, thresholds, intervals) lives in a config file,
  not in the code.

## Code and tests

- Python 3, standard library first. Use a virtual environment (`.venv`).
- Type hints on all functions. Short, clear names. Small functions.
- Write the test first for alert and analysis logic, using fake data.
  Use pytest. Run the tests after every change and show me the result.
- Tests must not call the real FMI API.
- Document every public function with a one-line docstring.

## Commands

- Set up: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Run tests: `pytest`
