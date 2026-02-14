# Smart Stock Recommendation App

## What This Is

A full-stack stock ranking application that uses a mathematically grounded quantitative algorithm to rank stocks across user-selected interest domains. Users pick domains (from a curated list or custom), and the app fetches real Yahoo Finance data every 5 minutes to produce top-5 stocks per domain and a single "Best Overall Investment Today." React frontend, algorithm-optimized backend.

## Core Value

The ranking algorithm must be mathematically sound, explainable, and produce defensible stock recommendations — algorithm quality is the product.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] User can select interest domains from a curated list (~10-15: AI, Sports, Semiconductors, Fintech, etc.)
- [ ] User can define custom domains mapped to relevant stocks
- [ ] App fetches real market data from Yahoo Finance every 5 minutes
- [ ] Quantitative ranking algorithm using: price momentum, volume changes, volatility, sector relative strength, financial ratios
- [ ] Stocks are normalized and scored via a single weighted ranking function
- [ ] App displays top 5 stocks per selected domain
- [ ] App displays a single "Best Overall Investment Today"
- [ ] Mathematical explanation of how each score is computed
- [ ] Historical scores stored and daily performance tracked
- [ ] Simple auth — login to save domain preferences
- [ ] Desktop + mobile responsive, clean fintech style
- [ ] Deployable on Hostinger VPS

### Out of Scope

- Machine learning / neural network models — prioritize explainable math
- Social sentiment analysis — keep signals market-data-only
- Trading execution / portfolio management — recommendation only
- Real-time websocket streaming — 5-min polling is sufficient

## Current Milestone: v1.0 Smart Stock Ranker

**Goal:** Build a working stock ranking app with real Yahoo Finance data, quantitative algorithm, domain selection, and responsive UI.

**Target features:**
- Domain selection from curated list (~10-15) + custom domains
- Real Yahoo Finance data fetching every 5 minutes with caching
- Quantitative ranking algorithm (momentum, volume, volatility, sector strength, ratios)
- Top 5 stocks per domain + "Best Overall Investment Today"
- Mathematical score explanations
- Historical score tracking + daily performance
- Simple auth (login to save preferences)
- Desktop + mobile responsive fintech UI
- Deployable on Hostinger VPS

## Context

- Data source: Yahoo Finance (free, no API key, some rate limits)
- Frontend: React (user preference)
- Backend: TBD during research — optimize for algorithm performance (likely Python/FastAPI)
- Target deployment: Hostinger VPS after local development
- This is a small app — algorithm correctness > UI polish > feature count
- Git workflow: commit at each phase, branch per phase

## Constraints

- **Data**: Yahoo Finance free tier — rate limits apply, need caching strategy
- **Budget**: Free APIs only, Hostinger VPS for hosting
- **Scope**: Small app — no over-engineering, no fake ML
- **Algorithm**: Must be mathematically grounded with explainable scoring

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Yahoo Finance for data | Free, no API key, sufficient for 5-min updates | — Pending |
| React for frontend | User preference | — Pending |
| Algorithm-first priority | Core value is the ranking quality, not UI | — Pending |
| Fixed + custom domains | Curated list for quick start, custom for flexibility | — Pending |

---
*Last updated: 2026-02-15 after milestone v1.0 start*
