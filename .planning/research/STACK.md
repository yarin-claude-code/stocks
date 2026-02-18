# Stack Research

**Date:** 2026-02-17

## Chosen Stack

| Layer | Choice | Notes |
|-------|--------|-------|
| Backend | Python 3.11+ / FastAPI 0.115+ | Async, auto OpenAPI, pandas/numpy ecosystem |
| Frontend | React 18+ / Vite 5+ | User preference; Vite not CRA (deprecated) |
| Data | yfinance >=1.0 | Free, no key, batch download |
| DB | SQLite → Supabase Postgres | Migrated Phase 01.1 |
| Scheduler | APScheduler 3.x (<4.0) | 4.x pre-release, breaking API |
| Charts | recharts 2.12+ | React-native, good for score bars |
| Styling | Tailwind 3.4+ | Responsive fintech UI |
| State | zustand | Lightweight vs Redux |

## Avoid

- Create React App (deprecated → Vite)
- APScheduler 4.x (pre-release, breaking)
- Celery/Redis (overkill for one scheduled task)
- pandas-datareader (deprecated Yahoo support)
- Django (over-engineered for API-only)
