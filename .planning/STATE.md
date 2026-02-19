# GSD State

## Current Position

Phase: 03 — API & Dashboard
Plan: 3/3
Status: Phase 03 complete
Last activity: 2026-02-20 — Plan 03-03 executed
Stopped at: Completed 03-03-PLAN.md

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
| DOMAIN_GROUPS removed | Phase 3 reads domains from DB via selectinload(Domain.stocks) |
| Raw factor values in DB | RankingResult stores raw (not normalized) factor values |
| scalar_subquery for latest computed_at | Single query, DB computes max — used in /api/rankings |
| 404 for unknown domain | GET /api/rankings/{domain} returns 404 when domain missing or empty |
| Tailwind v4 no-config | @tailwindcss/vite plugin — @import "tailwindcss" only, no tailwind.config.js |
| StockRanking shared type | Defined in BestOverall.tsx, re-exported for StockCard/ScoreBreakdown |

## Performance

| Phase | Plan | Duration | Files |
|-------|------|----------|-------|
| 01 | 01 | 25min | 13 |
| 01 | 02 | 15min | 4 |
| 01 | 03 | 15min | 5 |
| 01.1 | 01 | 35min | 7 |
| 02 | 01 | 3min | 2 |
| 02 | 02 | 8min | 2 |
| 03 | 01 | 20min | 5 |
| 03 | 02 | 15min | 3 |
| 03 | 03 | 15min | 11 |
