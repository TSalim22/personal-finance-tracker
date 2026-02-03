# Personal Finance Tracker

Track income and expenses, view spending charts and export a CSV.

## Try it in your browser

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/TSalim22/personal-finance-tracker?quickstart=1)

Sign in to GitHub, open a Codespace and wait for setup. Then run this in its terminal:

```sh
python app.py
```

Open port 5000 from the **Ports** tab if the app does not open automatically.

Codespaces uses your GitHub account’s allowance. Stop it when finished.

## Run it

Python 3.12 or later. Run these commands from the project folder:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python app.py
```

On macOS or Linux, activate with `source .venv/bin/activate` instead.

## How to use it

Open http://127.0.0.1:5000 and create an account.

Add income and expenses, choose a category, and filter by month. You can edit records and export the current view.

SQLite works by default. For PostgreSQL, copy `.env.example` to `.env` and set `DATABASE_URL`. To use the supplied database container, set a random `SECRET_KEY` in `.env` and run `docker compose up --build`.

Database tests recreate their tables. Use a disposable database for `TEST_DATABASE_URL`.

## Tests

```sh
python -m pytest -q
```

## Docker (optional)

```sh
docker build -t personal-finance-tracker .
docker run --rm -p 127.0.0.1:5000:5000 personal-finance-tracker
```

Use a volume for saved data. Docker hasn't been tested locally.
