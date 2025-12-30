# Copilot / Agent instructions for backend_basis

Short, actionable notes to help an AI agent be productive in this repository.

## Big picture
- This is a small monolithic prototype: a Flask API (`server.py`) serving a SQLAlchemy-backed model (`datenmodell.py`) with business logic in `service.py`. A minimal Streamlit frontend lives in `app_frontend.py`. Utility/demo scripts: `main.py`, `verwaltung.py` (manual DB interactions), and `test_client.py` (simple integration tests via HTTP).
- Data flow: frontend or `test_client.py` -> HTTP -> `server.py` endpoints -> `service.py` -> SQLAlchemy -> `fabrik.db` (SQLite file created by `datenmodell.py`).

## How to run / quick commands
- Install dependencies (example):
  - python -m venv .venv && source .venv/bin/activate
  - pip install flask sqlalchemy streamlit requests pandas
- Create DB tables:
  - python datenmodell.py  # runs Base.metadata.create_all(engine)
- Seed data (NOTE: see Known issues):
  - python verwaltung.py
- Start backend API:
  - python server.py  # Flask debug server on port 5000
- Run the frontend (in a separate terminal):
  - streamlit run app_frontend.py
- Run the simple HTTP tests / examples:
  - python test_client.py
- Run the demo script that uses `service` directly:
  - python main.py

## Concrete repository patterns and conventions
- Language / messages: code and printed messages are written in German; maintain German for logs and user-facing strings for consistency (e.g., `service.maschine_erstellen` prints German messages).
- DB sessions: use `Session = sessionmaker(bind=engine)` and create a new `session = Session()` per operation, then `session.close()` in `finally` blocks (see `service.py`). Follow this pattern when adding DB operations.
- Duplicate detection: `service.maschine_erstellen` expects `name` to be unique and handles `IntegrityError` to detect duplicates (returns False and prints a German error). When adding creation flows, preserve this style of returning boolean + logging.
- API contract:
  - GET `/maschinen` -> list of objects: {id, name, standort, status}
  - POST `/maschinen` with JSON {name, standort} -> 201 or 400 if name exists
  - POST `/stoerung/<id>` -> sets status to `STÖRUNG`
- Minimal test approach: `test_client.py` is the project's de-facto integration test; use it to validate API changes quickly.

## Known issues & upgrade notes
- Bug: `verwaltung.py` mistakenly calls `session.commit` without parentheses. Fix by changing `session.commit` to `session.commit()` so inserted rows actually persist.
- `datenmodell.py` uses `create_engine('sqlite:///fabrik.db', echo=True)`. `echo=True` is useful for debugging (prints SQL); if noise is a problem, set `echo=False`.
- `service.status_aendern` uses `session.query(Maschine).get(maschinen_id)`. In newer SQLAlchemy versions prefer `session.get(Maschine, id)`; consider migrating for compatibility.
- There's no `requirements.txt` or pinned dependencies — adding one will improve reproducibility.

## Suggestions for PRs / changes (concrete, small tasks an agent can implement)
- Add a `requirements.txt` listing packages used here and a short `README.md` with the same run steps.
- Fix `verwaltung.py` (`session.commit()`), then run `python verwaltung.py` to confirm records are persisted.
- Implement a minimal UI in `app_frontend.py` that fetches `/maschinen` and shows a table (use `requests` + `pandas.DataFrame` + `st.table`) and provides a button or form to call `/stoerung/<id>`.
- Add a simple unit or integration test for `service.maschine_erstellen` and `service.status_aendern` (use a temporary SQLite file or in-memory DB).

## Things NOT to change without discussing
- Changing message language from German to English: keep consistent with existing strings unless the repository owner asks.
- Changing the DB engine string (sqlite -> postgres): this is a major change and should be accompanied by migrations and new instructions.

---
If you'd like, I can (pick one):
- Add/fix `requirements.txt` and `README.md` with the run steps above ✅
- Implement the `verwaltung.py` commit fix and run the script to verify persistence ✅
- Start a small Streamlit UI in `app_frontend.py` that lists machines and adds a "Report Störung" action ✅

Please tell me which of the above you'd like me to do next or point out anything missing/unclear in this file.