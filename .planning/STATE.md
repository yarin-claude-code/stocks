# GSD State

## Current Position

Phase: 01.1 — SQLite to Supabase Postgres Migration
Plan: 1 (01.1-01-PLAN.md) — COMPLETE
Status: Phase 01.1 complete — all 1 plan executed
Last activity: 2026-02-18 — Plan 01.1-01 executed (SQLite to Supabase Postgres migration)

## Accumulated Context

### Roadmap Evolution

- Phase 01.1 inserted after Phase 1: SQLite to Supabase Postgres Migration (URGENT)

### Decisions

- **SQLAlchemy 2.0 Mapped syntax** — Used `Mapped[T]` / `mapped_column` (not legacy Column) for type-safe models
- **Alembic async migrations** — `async_engine_from_config` + `asyncio.run` in `run_migrations_online`
- **Idempotent seed** — `seed_db()` uses select-then-insert to avoid duplicate errors on re-runs
- **FastAPI lifespan** — Using `@asynccontextmanager` lifespan (not deprecated `@app.on_event`)
- **Single yf.download() batch call** — Avoids per-ticker rate limiting and latency
- **math.isnan() for validation** — Pure function, no pandas dependency in validate_ticker_data()
- **fetch_all_stocks silent fallback** — Returns {} on ANY exception, never raises to caller
- **BackgroundScheduler (sync)** — yfinance is sync; AsyncIOScheduler would block the event loop
- **Two-engine pattern (Postgres)** — async engine (asyncpg) for FastAPI, sync engine (psycopg2) for scheduler thread
- **scheduler.shutdown(wait=False)** — Prevents blocking app shutdown during active fetch
- **sync_database_url property on Settings** — Derives psycopg2 URL from asyncpg URL; single source of truth
- **Alembic URL via config.set_main_option** — configparser %(VAR)s interpolation cannot read env vars; inject programmatically in env.py after load_dotenv()
- **Supabase direct port 5432** — Not pgbouncer 6543; required for SQLAlchemy session mode compatibility

## Performance Metrics

| Phase | Plan | Duration | Tasks | Files |
|-------|------|----------|-------|-------|
| 01    | 01   | 25min    | 2     | 13    |
| 01    | 02   | 15min    | 2     | 4     |
| 01    | 03   | 15min    | 2     | 5     |
| 01.1  | 01   | 35min    | 3     | 7     |
