# Phase 1: Data Pipeline Foundation — Research Summary

**Date:** 2026-02-17 | **Status:** COMPLETE (implemented)

## Key Findings

| Topic | Finding |
|-------|---------|
| yfinance | Use `yf.download(tickers_list, ...)` — one batch call, never per-ticker loop |
| Rate limits | ~200-400 req/hr; batch download reduces N requests → 1 per cycle |
| MultiIndex access | `raw["Close"][ticker]` — not `raw[ticker]["Close"]` (default `group_by="column"`) |
| APScheduler | Use 3.x (`<4.0`); 4.x is pre-release with breaking API changes |
| Scheduler type | `BackgroundScheduler` (sync) — yfinance is sync; don't block the event loop |
| FastAPI lifespan | `@asynccontextmanager` lifespan — not deprecated `@app.on_event` |
| SQLAlchemy | 2.0 style: `Mapped[T]` / `mapped_column`, not legacy `Column` |
| SQLite WAL | `PRAGMA journal_mode=WAL` via `event.listens_for` on connect |
| Alembic | Set up in Phase 1 — retrofitting later is painful |
| Fallback | `fetch_all_stocks()` returns `{}` on any exception; DB retains last-known-good |
| Timestamp | Store `fetched_at` UTC on every row; expose via `/api/health` |

## Pitfalls

- `yf.Ticker(t).history()` in a loop → rate limited immediately
- `@app.on_event("startup")` → deprecated since FastAPI 0.93
- APScheduler 4.x → `BackgroundScheduler` doesn't exist, breaking API
- Multi-worker uvicorn → each worker starts its own scheduler (run `--workers 1`)
- pandas 2.2 tz mismatch → normalize index with `.tz_localize(None)` after download

## Stack (all already in requirements.txt)

`yfinance>=1.0`, `sqlalchemy>=2.0`, `apscheduler>=3.10,<4.0`, `fastapi`, `alembic`, `pandas>=2.2`, `aiosqlite` (replaced by asyncpg in Phase 01.1)
