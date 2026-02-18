# Smart Stock Recommendation App

**Core value:** Mathematically grounded, explainable stock ranking algorithm.
**Stack:** FastAPI + React + Supabase Postgres + yfinance
**Milestone:** v1.0 Smart Stock Ranker
**Deployment:** Hostinger VPS

## Requirements (Active)

- Domain selection from curated list (~10-15: AI, Sports, Semiconductors, Fintech, etc.)
- Custom domains mapped to user-selected stocks
- Yahoo Finance data every 5 minutes
- Quantitative ranking: momentum, volume, volatility, relative strength, financial ratios
- Top 5 stocks per domain + "Best Overall Investment Today"
- Score breakdown (per-factor explanation)
- Historical score tracking
- Simple auth (save domain preferences)
- Desktop + mobile responsive, fintech style

## Out of Scope

- ML/neural networks, social sentiment, websocket streaming, trading execution

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Yahoo Finance | Free, no API key |
| React frontend | User preference |
| Algorithm-first | Core product value |
| 5-min polling | Sufficient, simple |

*Last updated: 2026-02-15*
