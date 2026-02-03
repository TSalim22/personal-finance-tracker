# Personal Finance Tracker

Track income and spending with accounts, charts and CSV export.

This is a small, independent Python portfolio project. The code favours ordinary functions and clear modules over complex architecture.

## Setup

Requires Python 3.12+ (desktop tools also require Tkinter, included with the standard Windows Python installer).

```sh
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux instead: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python app.py
```

Run commands from this repository's root. Web apps bind to localhost by default. Each app is independent, so stop one before starting another on the same port.

## Check it

```sh
python -m pytest -q
```

## Dates

The commit author dates have been deliberately arranged between October 2025 and October 2026 at the portfolio owner's request. They are presentation metadata, not a record of the actual development timeline. Repository creation and upload timestamps remain the real dates.

## Try it

Open http://127.0.0.1:5000 and register. Add income and expenses with categories and dates. The dashboard calculates a balance using decimal arithmetic, groups expenses by category and plots them using a bundled copy of Chart.js. Filter a month, edit a record or export the current view as CSV. The CSV guards descriptions against spreadsheet formula interpretation.

SQLite is the default for an easy local start. To use PostgreSQL, copy `.env.example` to `.env`, set `DATABASE_URL` to your local PostgreSQL database, and restart. `compose.yml` supplies a local PostgreSQL database and the app together. The CI workflow runs the same account and finance tests against SQLite and PostgreSQL. `db.create_all()` creates a fresh schema; this small project does not have a migration system.

## Optional local container

```sh
docker build -t personal-finance-tracker .
docker run --rm -p 127.0.0.1:5000:5000 personal-finance-tracker
```

This runs a local demonstration server. Container storage is temporary unless you mount a volume for `instance/`. Docker commands were supplied but Docker is not installed in the development environment, so container execution was not verified here.

For Compose, put a long random `SECRET_KEY` in `.env` first. The supplied database password is for the isolated local demo only. PostgreSQL tests use a disposable database via `TEST_DATABASE_URL`; never point that variable at a database containing real data because the test fixture recreates its tables.
