# GSD State

## Current Position

Phase: 02 — Ranking Algorithm
Status: Phase 02 complete — 2/2 plans executed
Last activity: 2026-02-18 — Plan 02-02 executed

## Key Decisions

| Decision | Detail |
|----------|--------|
| SQLAlchemy 2.0 | `Mapped[T]` / `mapped_column` — not legacy Column |
| Two-engine pattern | asyncpg (FastAPI) + psycopg2 (scheduler) |
| BackgroundScheduler | yfinance is sync — AsyncIOScheduler would block event loop |
| FastAPI lifespan | `@asynccontextmanager` — not deprecated `@app.on_event` |
| yf.download() batch | Avoids per-ticker rate limits |
| fetch_all_stocks fallback | Returns `{}` on any exception, never raises |
| Supabase port 5432 | Not 6543 (pgbouncer) — required for SQLAlchemy session mode |
| epsilon guard (1e-12) | np.std of identical floats returns ~6.9e-18, not exactly 0 |
| ddof=0 | Population std for Z-score normalization |
| Pre-invert volatility/PE | Inverted in compute_factors_for_ticker() before rank_domain() |
| DOMAIN_GROUPS in fetch_cycle() | Hardcoded for Phase 2 — Phase 3 replaces with DB query |
| Second yf.download() in fetch_cycle() | Simpler than refactoring fetch_all_stocks() |

## Performance

| Phase | Plan | Duration | Files |
|-------|------|----------|-------|
| 01 | 01 | 25min | 13 |
| 01 | 02 | 15min | 4 |
| 01 | 03 | 15min | 5 |
| 01.1 | 01 | 35min | 7 |
| 02 | 01 | 3min | 2 |
| 02 | 02 | 8min | 2 |
