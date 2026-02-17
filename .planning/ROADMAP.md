# Roadmap: Smart Stock Recommendation App

**Milestone:** v1.0 Smart Stock Ranker
**Goal:** Build a working stock ranking app with real Yahoo Finance data, quantitative algorithm, domain selection, and responsive UI.
**Created:** 2026-02-17
**Stack:** Python/FastAPI + React/Vite + SQLite + yfinance

---

## Phase 1: Data Pipeline Foundation

**Goal:** Reliable Yahoo Finance integration with caching, scheduling, and graceful degradation — the foundation everything else depends on.

**Requirements covered:** DATA-01, DATA-02, DATA-03, DATA-04, DATA-05

**Delivers:**
- Project structure (backend + frontend scaffolding)
- SQLite schema (stocks, scores, domains, score_snapshots)
- yfinance batch download integration
- APScheduler 5-minute polling cycle
- Error handling + fallback to last known good data
- "Last updated" timestamp tracking
- Health check endpoint

**Architecture:**
- `backend/services/data_fetcher.py` — yfinance batch fetching, caching
- `backend/models/` — SQLAlchemy models (Stock, Domain, ScoreSnapshot)
- `backend/scheduler.py` — APScheduler setup in FastAPI lifespan

**Research needed:** No (standard yfinance + APScheduler patterns)

---

## Phase 2: Ranking Algorithm

**Goal:** Mathematically sound, explainable scoring engine — the core product differentiator.

**Requirements covered:** ALGO-01, ALGO-02, ALGO-03, ALGO-04, ALGO-05, ALGO-06

**Delivers:**
- Z-score normalization per factor with ±3 std dev outlier capping
- Five scoring factors: price momentum, volume change, volatility, sector relative strength, financial ratios
- Weighted composite score (0–100 scale) with documented weight rationale
- Peer group ranking (within domain, not globally)
- Score breakdown data structure (per-factor contributions)
- Comprehensive pytest test suite for edge cases (1 stock, extreme values, NaN)

**Architecture:**
- `backend/services/ranking_engine.py` — isolated, testable scoring module
- Clear pipeline: normalize → weight → rank → store
- Factor weights documented in code comments with rationale

**Research needed:** Yes — `/gsd:research-phase 2` for quantitative normalization best practices and factor weight selection methodologies

---

## Phase 3: API & Dashboard

**Goal:** Functional React dashboard displaying ranked stocks — the MVP that proves the product works.

**Requirements covered:** UI-01, UI-02, UI-03, UI-04, UI-05, DOM-01, DOM-02

**Delivers:**
- FastAPI routes: `/rankings`, `/rankings/{domain}`, `/domains`, `/health`
- React dashboard with domain selector (curated list hardcoded)
- Top 5 stock cards per domain with scores
- "Best Overall Investment Today" hero section
- Score breakdown visualization (recharts bar chart)
- Loading/skeleton states during refresh
- "Market Closed" banner outside trading hours
- Mobile-responsive layout (Tailwind CSS)

**Architecture:**
- `backend/routers/rankings.py`, `backend/routers/domains.py`
- `frontend/src/components/` — Dashboard, DomainSelector, StockCard, ScoreBreakdown, BestOverall
- CORS configured for local dev

**Research needed:** No (standard FastAPI + React integration)

---

## Phase 4: Authentication & Personalization

**Goal:** User accounts with saved domain preferences — adds stickiness and enables personalization.

**Requirements covered:** AUTH-01, AUTH-02, AUTH-03, AUTH-04

**Delivers:**
- User registration and login (email + password)
- JWT token auth (python-jose, passlib/bcrypt)
- Session persistence across browser refresh (JWT in localStorage)
- Saved domain selections per user
- Protected endpoints for preference management

**Architecture:**
- `backend/routers/auth.py`
- `backend/services/auth_service.py`
- `backend/models/user.py` — User SQLAlchemy model
- Frontend: login/register page, auth context, protected routes

**Research needed:** No (standard FastAPI JWT auth pattern)

---

## Phase 5: Historical Tracking & Custom Domains

**Goal:** Score history visualization and user-defined domains — depth features that increase long-term value.

**Requirements covered:** HIST-01, HIST-02, HIST-03, DOM-03, DOM-04

**Delivers:**
- Daily score snapshots stored automatically
- Historical score chart per stock (recharts line chart)
- Score trend indicators (rising/falling) on dashboard
- Custom domain creation (user-defined name + ticker list)
- Ticker validation against Yahoo Finance before accepting
- Survivorship bias disclaimer on historical views

**Architecture:**
- `backend/routers/history.py`
- `backend/routers/custom_domains.py`
- ScoreSnapshot table with date + ticker + score
- Efficient time series queries with SQLite indexing

**Research needed:** Yes — `/gsd:research-phase 5` for SQLite time series storage patterns and efficient trend query strategies

---

## Requirement Traceability

| Requirement | Phase |
|-------------|-------|
| DATA-01 | 1 |
| DATA-02 | 1 |
| DATA-03 | 1 |
| DATA-04 | 1 |
| DATA-05 | 1 |
| ALGO-01 | 2 |
| ALGO-02 | 2 |
| ALGO-03 | 2 |
| ALGO-04 | 2 |
| ALGO-05 | 2 |
| ALGO-06 | 2 |
| DOM-01 | 3 |
| DOM-02 | 3 |
| DOM-03 | 5 |
| DOM-04 | 5 |
| UI-01 | 3 |
| UI-02 | 3 |
| UI-03 | 3 |
| UI-04 | 3 |
| UI-05 | 3 |
| AUTH-01 | 4 |
| AUTH-02 | 4 |
| AUTH-03 | 4 |
| AUTH-04 | 4 |
| HIST-01 | 5 |
| HIST-02 | 5 |
| HIST-03 | 5 |

**Coverage:** 27/27 requirements mapped ✓

---

## Phase Ordering Rationale

1. **Data first** — nothing works without reliable Yahoo Finance integration; rate limiting is the #1 technical risk
2. **Algorithm second** — the ranking engine IS the product; must be correct and tested before building UI around it
3. **Dashboard third** — proves MVP value with functional ranked stock display
4. **Auth fourth** — adds stickiness and user context needed for personalization
5. **History + custom domains last** — depth features that require auth foundation

---

*Roadmap created: 2026-02-17*
*Last updated: 2026-02-17 after research synthesis*
