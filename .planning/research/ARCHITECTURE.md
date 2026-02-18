# Architecture Research

**Date:** 2026-02-17

## Core Pattern: Precomputed Rankings

APScheduler (5 min) → yfinance batch fetch → ranking_engine → DB → API serves cached results.
Never compute on request path.

## Data Flow

```
[APScheduler: 5 min] → [data_fetcher.py: yf.download()] → [ranking_engine.py: normalize/score]
    → [DB: store snapshots] → [API request] → [serve precomputed scores]
```

## Key Boundaries

| Boundary | Rule |
|----------|------|
| ranking_engine.py | Pure — no DB, no yfinance, no I/O |
| data_fetcher.py | yfinance only — no scoring logic |
| scheduler.py | Orchestrates fetch → compute → store |
| API routes | Read from DB only — never call yfinance |
| Async sessions | FastAPI routes only |
| Sync sessions | Scheduler thread only |

## Anti-Patterns

- Fetching yfinance on each API request → rate limited, slow
- Monolithic fetch+score function → untestable
- Async session in scheduler or sync session in routes → engine mismatch
