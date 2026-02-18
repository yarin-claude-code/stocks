# Requirements: Smart Stock Ranker v1.0

**Core value:** Explainable math-based stock ranking.

## v1.0

| ID | Requirement | Phase | Status |
|----|-------------|-------|--------|
| DATA-01 | Batch fetch from Yahoo Finance every 5 min | 1 | ✓ |
| DATA-02 | Cache in DB | 1, 01.1 | ✓ |
| DATA-03 | Fallback to last-known-good on fetch failure | 1 | ✓ |
| DATA-04 | Validate fetched data (no NaN/empty) | 1 | ✓ |
| DATA-05 | Display "last updated" timestamp | 1 | ✓ |
| ALGO-01 | 5-factor composite score | 2 | ✓ |
| ALGO-02 | Z-score normalization ±3σ cap | 2 | ✓ |
| ALGO-03 | Weighted score 0–100 per stock | 2 | ✓ |
| ALGO-04 | Top 5 stocks per domain | 2 | ✓ |
| ALGO-05 | "Best Overall Investment Today" | 2 | ✓ |
| ALGO-06 | Per-factor score breakdown | 2 | ✓ |
| DOM-01 | Curated domain list (~10-15) | 3 | — |
| DOM-02 | Domain → ticker mapping | 3 | — |
| DOM-03 | Custom domains | 5 | — |
| DOM-04 | Ticker validation | 5 | — |
| UI-01 | Responsive dashboard with top 5 per domain | 3 | — |
| UI-02 | Click stock → score breakdown | 3 | — |
| UI-03 | Loading/skeleton states | 3 | — |
| UI-04 | "Market Closed" banner | 3 | — |
| UI-05 | Desktop + mobile | 3 | — |
| AUTH-01 | Register email/password | 4 | — |
| AUTH-02 | Login + JWT | 4 | — |
| AUTH-03 | Session persistence | 4 | — |
| AUTH-04 | Save domain preferences | 4 | — |
| HIST-01 | Daily score snapshots | 5 | — |
| HIST-02 | Score history chart | 5 | — |
| HIST-03 | Trend indicators | 5 | — |

## Out of Scope
ML predictions, sentiment, real-time streaming, portfolio tracking, trading execution, backtesting.

## v2 (deferred)
Alerts (NOTF-01, NOTF-02), stock comparison, configurable weights, additional data sources.

*Defined: 2026-02-17*
