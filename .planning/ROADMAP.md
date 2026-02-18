# Roadmap: Smart Stock Ranker v1.0

**Stack:** FastAPI + React + Supabase Postgres + yfinance
**Created:** 2026-02-17 | **Updated:** 2026-02-18

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
- Plans: TBD

## Phase 4: Authentication & Personalization
User accounts with saved domain preferences via Supabase Auth.
- `supabase-auth` package (NOT gotrue — deprecated Aug 2025)
- Plans: TBD

## Phase 5: Historical Tracking & Custom Domains
Daily score snapshots, trend charts, user-defined domains with ticker validation.
- Plans: TBD

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

*Updated: 2026-02-18*
