# Roadmap: Smart Stock Ranker v1.0

**Stack:** FastAPI + React + Supabase Postgres + yfinance
**Created:** 2026-02-17 | **Updated:** 2026-02-20

---

## Phase 1: Data Pipeline Foundation ✓
Reliable Yahoo Finance integration — caching, scheduling, graceful degradation.
- SQLAlchemy models, Alembic, yfinance batch download, APScheduler, health endpoint
- Plans: 3/3 complete

## Phase 01.1: SQLite → Supabase Migration ✓
- asyncpg (async engine) + psycopg2 (scheduler sync engine), Alembic to Supabase
- Plans: 1/1 complete

## Phase 2: Ranking Algorithm ✓
Pure scoring engine — normalize, weight, scale, rank.
- Z-score normalization, 5 factors, weighted composite (0–100), peer-group ranking
- Plans: 2/2 complete

## Phase 3: API & Dashboard
FastAPI routes + React dashboard showing ranked stocks.
- Routes: `/rankings`, `/rankings/{domain}`, `/domains`, `/health`
- Components: DomainSelector, StockCard, ScoreBreakdown, BestOverall
- **Plans:** 3/4 complete
  - [x] 03-01-PLAN.md — RankingResult model + Alembic migration + seed expansion + fetch_cycle DB persistence
  - [x] 03-02-PLAN.md — FastAPI routes (/api/domains, /api/rankings, /api/rankings/{domain}) + CORS
  - [x] 03-03-PLAN.md — React frontend scaffold + all dashboard components
  - [ ] 03-04-PLAN.md — Human verification of full dashboard UI

## Phase 4: Authentication & Personalization
User accounts with saved domain preferences via Supabase Auth.
- `supabase-auth` package (NOT gotrue — deprecated Aug 2025)
- **Plans:** 5 plans
  - [ ] 04-01-PLAN.md — Backend config + get_current_user dependency + user_preferences migration + CORS update
  - [ ] 04-02-PLAN.md — GET/PUT /api/preferences router
  - [ ] 04-03-PLAN.md — TanStack Router + Supabase client + login/register pages + protected dashboard
  - [ ] 04-04-PLAN.md — Load/save domain preferences on login and domain change
  - [ ] 04-05-PLAN.md — Human verification of full auth + preferences flow

## Phase 5: Historical Tracking & Custom Domains
Daily score snapshots, trend charts, user-defined domains with ticker validation.
- **Plans:** 5 plans
  - [ ] 05-01-PLAN.md — DailySnapshot model + Alembic migration + snapshot_job + compute_trend
  - [ ] 05-02-PLAN.md — user_domains/user_domain_tickers models + migration + RLS + CRUD routes
  - [ ] 05-03-PLAN.md — GET /api/history/{ticker} + ScoreHistoryChart + TrendBadge + /history/:ticker route
  - [ ] 05-04-PLAN.md — CustomDomainManager UI + /domains/custom route
  - [ ] 05-05-PLAN.md — Human verification of all Phase 5 features

---

## Requirement Coverage: 27/27 ✓

| Req group | Phase |
|-----------|-------|
| DATA-01–05 | 1, 01.1 |
| ALGO-01–06 | 2 ✓ |
| DOM-01–02 | 3 |
| DOM-03–04 | 5 |
| UI-01–05 | 3 |
| AUTH-01–04 | 4 |
| HIST-01–03 | 5 |

*Updated: 2026-02-20*
