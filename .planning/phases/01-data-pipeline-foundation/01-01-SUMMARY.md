---
phase: 01-data-pipeline-foundation
plan: "01"
subsystem: database
tags: [fastapi, sqlalchemy, aiosqlite, alembic, pydantic-settings, python]

requires: []
provides:
  - Async SQLite database engine with WAL mode (aiosqlite + SQLAlchemy 2.0)
  - ORM models: Domain, Stock, ScoreSnapshot
  - FastAPI app skeleton with lifespan context manager
  - Alembic migrations configured for async engine
  - DB seed: 3 domains, 9 stocks (AI/Tech, EV, Finance)
affects:
  - 01-02 (yfinance fetcher uses Stock model + get_db session)
  - 01-03 (APScheduler job uses same session factory)
  - all subsequent phases (app.main, models, database are the foundation)

tech-stack:
  added:
    - fastapi>=0.115
    - uvicorn[standard]>=0.29
    - sqlalchemy>=2.0
    - aiosqlite>=0.20
    - alembic>=1.13
    - pydantic-settings>=2.0
    - apscheduler>=3.10,<4.0
    - yfinance>=1.0
    - pandas>=2.2
    - python-dotenv>=1.0
  patterns:
    - SQLAlchemy 2.0 Mapped/mapped_column declarative style
    - AsyncSession via async_sessionmaker with expire_on_commit=False
    - WAL mode enabled via sync_engine event listener
    - FastAPI lifespan (not deprecated @app.on_event)
    - Pydantic BaseSettings for env-driven config

key-files:
  created:
    - backend/requirements.txt
    - backend/.env.example
    - backend/app/__init__.py
    - backend/app/config.py
    - backend/app/main.py
    - backend/app/database.py
    - backend/app/models/__init__.py
    - backend/app/models/stock.py
    - backend/app/models/score_snapshot.py
    - backend/alembic.ini
    - backend/alembic/env.py
    - backend/alembic/versions/81cb55ab1baf_initial_schema.py
    - backend/.gitignore
  modified: []

key-decisions:
  - "Used SQLAlchemy 2.0 Mapped syntax (not legacy Column) for type-safe models"
  - "WAL mode enabled at connect-time via sync_engine event for concurrent reads"
  - "Alembic configured with async_engine_from_config + asyncio.run for online migrations"
  - "seed_db() uses select+flush pattern to avoid duplicate key errors on re-runs"
  - "Generated initial migration and ran upgrade head so alembic check passes clean"

patterns-established:
  - "Async engine: create_async_engine + async_sessionmaker(expire_on_commit=False)"
  - "Dependency injection: get_db() as async generator yielding AsyncSession"
  - "App lifecycle: lifespan context manager (create_all then seed_db)"
  - "Config: BaseSettings reads DATABASE_URL and FETCH_INTERVAL_MINUTES from .env"

requirements-completed:
  - DATA-02

duration: 25min
completed: 2026-02-17
---

# Phase 01 Plan 01: Backend Scaffold and Database Foundation Summary

**Async SQLite backend with FastAPI skeleton, SQLAlchemy 2.0 ORM models (Domain, Stock, ScoreSnapshot), Alembic async migrations, and seeded 9-stock dataset across 3 domains**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-02-17T00:00:00Z
- **Completed:** 2026-02-17
- **Tasks:** 2
- **Files created:** 13

## Accomplishments

- FastAPI app with lifespan context manager creates tables and seeds stock data on startup
- Async SQLite engine with WAL mode for concurrent read performance
- All three ORM models (Domain, Stock, ScoreSnapshot) using SQLAlchemy 2.0 Mapped syntax
- Alembic configured for async engine with autogenerate; initial migration generated and applied (alembic check clean)
- Seed function inserts 3 domains and 9 stocks idempotently on startup

## Task Commits

Each task was committed atomically:

1. **Task 1: Backend scaffold** - `9a77eda` (feat)
2. **Task 2: Alembic init + migration** - `f44bf30` (feat)
3. **Deviation: .gitignore** - `7d91e68` (chore)

**Plan metadata:** (this SUMMARY commit)

## Files Created/Modified

- `backend/requirements.txt` - All pinned dependencies including apscheduler<4.0
- `backend/.env.example` - DATABASE_URL and FETCH_INTERVAL_MINUTES
- `backend/app/config.py` - BaseSettings reading from .env
- `backend/app/database.py` - Async engine, WAL mode, Base, get_db, seed_db
- `backend/app/main.py` - FastAPI app with lifespan (create_all + seed_db)
- `backend/app/models/stock.py` - Domain and Stock SQLAlchemy 2.0 models
- `backend/app/models/score_snapshot.py` - ScoreSnapshot with ticker/fetched_at indexes
- `backend/app/models/__init__.py` - Exports Stock, Domain, ScoreSnapshot
- `backend/alembic.ini` - Points to sqlite+aiosqlite:///./stocks.db
- `backend/alembic/env.py` - Async engine + Base.metadata autogenerate
- `backend/alembic/versions/81cb55ab1baf_initial_schema.py` - Initial migration
- `backend/.gitignore` - Excludes __pycache__, *.db, *.db-shm, *.db-wal

## Decisions Made

- Used SQLAlchemy 2.0 `Mapped[T]` / `mapped_column` pattern (not legacy Column) for type safety
- WAL mode set via `event.listens_for(engine.sync_engine, "connect")` — correct approach for async engines
- Alembic `run_migrations_online` uses `async_engine_from_config` with `asyncio.run` wrapper
- Generated and applied initial migration so `alembic check` is clean from day one
- `seed_db()` uses `select().scalar_one_or_none()` + conditional insert to be idempotent

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added backend/.gitignore**
- **Found during:** Post-task cleanup
- **Issue:** stocks.db, __pycache__/ dirs would be tracked by git without a .gitignore
- **Fix:** Created backend/.gitignore excluding *.db, *.db-shm, *.db-wal, __pycache__
- **Files modified:** backend/.gitignore (new)
- **Verification:** git status shows no untracked DB or cache files
- **Committed in:** 7d91e68 (chore commit)

---

**Total deviations:** 1 auto-fixed (Rule 2 - missing critical)
**Impact on plan:** .gitignore is essential to prevent database files from being committed. No scope creep.

## Issues Encountered

- `alembic check` initially failed because the database didn't exist (no migrations applied). Fix: generated initial migration with `--autogenerate` and ran `upgrade head` first. Check now passes clean.

## User Setup Required

None - no external service configuration required. Database is SQLite, created automatically on first run.

## Next Phase Readiness

- async_session_maker, Base, get_db, Stock, Domain, ScoreSnapshot all importable
- Database initializes and seeds on first startup
- Ready for Plan 02: yfinance data fetcher using Stock model and get_db session

---
*Phase: 01-data-pipeline-foundation*
*Completed: 2026-02-17*
