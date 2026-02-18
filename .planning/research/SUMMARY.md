# Project Research Summary

**Project:** Smart Stock Ranker | **Date:** 2026-02-17

## Stack Decision

| Layer | Choice | Reason |
|-------|--------|--------|
| Backend | FastAPI + Python | Async, yfinance/pandas ecosystem, fast API |
| Frontend | React + Vite | User preference, component model fits dashboard |
| Data | yfinance | Free, no API key, batch download support |
| DB | SQLite → Supabase Postgres | Simple start, migrated Phase 01.1 |
| Scheduler | APScheduler 3.x | Simple interval jobs, no Celery/Redis overhead |
| Styling | Tailwind + recharts | Responsive fintech UI, score charts |

## Architecture

Precomputed rankings pattern: APScheduler (5 min) → yfinance batch fetch → ranking_engine → DB → API serves cached results. Never compute on request path.

## Feature Priority

**Must have:** score ranking 0–100, domain filtering, top 5 per domain, score breakdown, last-updated timestamp, mobile-responsive, auth + saved preferences

**Differentiators:** "Best Overall Investment Today", domain-based org (not GICS sectors), mathematical explanation, historical tracking, custom domains

**Deferred (v2+):** real-time streaming, ML predictions, sentiment, portfolio tracking, alerts, backtesting

## Key Risks

1. **Yahoo Finance reliability** — scraped API, breaks without notice. Mitigate: batch download, fallback to last-known-good, validate for NaN
2. **Algorithm credibility** — arbitrary weights destroy trust. Mitigate: document rationale, show per-factor breakdown in UI
3. **Stale data** — scheduler fails silently. Mitigate: always show `fetched_at` timestamp, health endpoint
4. **Normalization correctness** — wrong scale = one factor dominates. Mitigate: Z-score per factor, ±3σ cap, peer-group only
