---
phase: 01-data-pipeline-foundation
plan: "03"
subsystem: scheduler-and-health
tags: [apscheduler, fastapi, sqlalchemy, sqlite, python]

requires:
  - 01-01 (FastAPI app, SQLAlchemy models, async engine, database module)
  - 01-02 (fetch_all_stocks, SEED_TICKERS, data_fetcher service)
provides:
  - APScheduler BackgroundScheduler polling fetch_all_stocks every 5 minutes
  - fetch_cycle() — fetches data, upserts ScoreSnapshot rows, updates Stock.last_updated
  - GET /api/health — returns status, last_fetched, data_available, timestamp
  - Lifespan-managed scheduler start/stop (graceful shutdown)
  - seed.py — standalone async seed module extracted from database.py
affects:
  - All future phases that depend on live data being present in ScoreSnapshot

tech-stack:
  added:
    - apscheduler>=3.10,<4.0 (BackgroundScheduler + IntervalTrigger)
    - sqlalchemy sync engine (sqlite driver, separate from async aiosqlite engine)
  patterns:
    - Sync SQLAlchemy engine for background thread (scheduler runs outside async event loop)
    - Separate _sync_engine created from settings.database_url with aiosqlite replaced by sqlite
    - max_instances=1 on APScheduler job prevents overlapping fetches
    - Health endpoint uses func.max(ScoreSnapshot.fetched_at) for last-fetch timestamp

key-files:
  created:
    - backend/app/scheduler.py
    - backend/app/routers/__init__.py
    - backend/app/routers/health.py
    - backend/app/seed.py
  modified:
    - backend/app/main.py

key-decisions:
  - "BackgroundScheduler (sync) used — yfinance is sync and runs in background thread, not async event loop"
  - "Separate sync SQLite engine in scheduler — cannot use aiosqlite from non-async context"
  - "fetch_cycle returns early on empty data — last-known-good ScoreSnapshot rows are never deleted"
  - "seed_db extracted to seed.py — separates seed responsibility from database connection module"
  - "scheduler.shutdown(wait=False) — prevents blocking app shutdown if a fetch is in progress"

requirements-completed:
  - DATA-01
  - DATA-02
  - DATA-03
  - DATA-05

duration: 15min
completed: 2026-02-17
---

# Phase 01 Plan 03: APScheduler Polling and Health Check Summary

**APScheduler BackgroundScheduler wired into FastAPI lifespan polling yfinance every 5 minutes, with GET /api/health surfacing last-fetch timestamp — completing the full data pipeline**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-02-17
- **Completed:** 2026-02-17
- **Tasks:** 2
- **Files created:** 4 (scheduler.py, routers/__init__.py, routers/health.py, seed.py)
- **Files modified:** 1 (main.py)

## Accomplishments

- APScheduler BackgroundScheduler configured with 5-minute IntervalTrigger, max_instances=1
- fetch_cycle() writes ScoreSnapshot rows and updates Stock.last_updated per successful fetch
- No-data fallback: if fetch_all_stocks() returns {}, fetch_cycle returns without touching DB (last-known-good retained)
- GET /api/health returns {status, last_fetched, data_available, timestamp} — all four fields
- FastAPI lifespan starts scheduler on startup and calls scheduler.shutdown(wait=False) on stop
- App verified via ASGI test client: /api/health returns 200, /root returns 200

## Task Commits

| Task   | Name                                         | Commit  | Files                                                       |
|--------|----------------------------------------------|---------|-------------------------------------------------------------|
| Task 1 | APScheduler fetch_cycle with DB upsert       | 08fa696 | backend/app/scheduler.py                                    |
| Task 2 | Health endpoint + scheduler lifespan wiring  | 125d9ac | backend/app/routers/__init__.py, routers/health.py, seed.py, main.py |

## Files Created/Modified

- `backend/app/scheduler.py` — BackgroundScheduler, fetch_cycle, create_scheduler
- `backend/app/routers/__init__.py` — empty package marker
- `backend/app/routers/health.py` — GET /api/health with func.max(fetched_at) query
- `backend/app/seed.py` — async seed_db extracted from database.py
- `backend/app/main.py` — updated lifespan with scheduler start/stop + health router registration

## Decisions Made

- BackgroundScheduler (sync) not AsyncIOScheduler — yfinance is a sync library; running it in the async event loop would block it
- Separate `_sync_engine` created by replacing `sqlite+aiosqlite` with `sqlite` in the URL — async engine cannot be used from a background thread
- `max_instances=1` on the APScheduler job prevents concurrent overlapping fetches if a cycle takes longer than 5 minutes
- `seed_db` extracted to `backend/app/seed.py` — cleaner separation between DB connection (database.py) and seed logic
- `scheduler.shutdown(wait=False)` on lifespan exit — avoids blocking shutdown if a fetch is in progress

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Minor] seed_db import updated in main.py**
- **Found during:** Task 2
- **Issue:** Plan's main.py imports `from .seed import seed_db`, but original main.py imported `from .database import engine, Base, seed_db`. The seed_db in database.py had slightly different seed data than plan's seed.py spec.
- **Fix:** Created seed.py with matching SEED_DATA, updated main.py import to use seed.py. database.py seed_db left in place (unused, no breaking change).
- **Files modified:** backend/app/seed.py (new), backend/app/main.py (import updated)
- **Committed in:** 125d9ac

## Self-Check

- [x] `backend/app/scheduler.py` exists with create_scheduler() and fetch_cycle()
- [x] `backend/app/routers/health.py` exists with GET /api/health
- [x] `backend/app/main.py` contains scheduler.start() and include_router(health_router)
- [x] Commits 08fa696 (Task 1) and 125d9ac (Task 2) exist in git log
- [x] ASGI test: /api/health returns 200 with {status, last_fetched, data_available, timestamp}
- [x] python -c import test: scheduler creates one "data_fetch" job

## Self-Check: PASSED

---
*Phase: 01-data-pipeline-foundation*
*Completed: 2026-02-17*
