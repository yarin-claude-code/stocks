# Requirements: Smart Stock Recommendation App

**Defined:** 2026-02-17
**Core Value:** Mathematically grounded, explainable stock ranking algorithm — algorithm quality is the product.

## v1.0 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Data Pipeline

- [ ] **DATA-01**: App fetches stock price/volume data from Yahoo Finance in batch every 5 minutes
- [ ] **DATA-02**: App caches fetched data in database to avoid redundant API calls
- [ ] **DATA-03**: App falls back to last-known-good data when Yahoo Finance fetch fails
- [ ] **DATA-04**: App validates fetched data for completeness (no NaN, no empty results)
- [ ] **DATA-05**: App displays "last updated" timestamp on all data views

### Ranking Algorithm

- [ ] **ALGO-01**: App calculates composite score using 5 factors: price momentum, volume change, volatility, sector relative strength, financial ratios
- [ ] **ALGO-02**: App normalizes all factors via z-score normalization with outlier capping (±3 std dev)
- [ ] **ALGO-03**: App produces a single weighted score (0-100 scale) per stock
- [ ] **ALGO-04**: App displays the top 5 ranked stocks per selected domain
- [ ] **ALGO-05**: App displays a single "Best Overall Investment Today" across all domains
- [ ] **ALGO-06**: App shows mathematical breakdown of how each stock's score was computed (per-factor contribution)

### Domain System

- [ ] **DOM-01**: User can select interest domains from a curated list (~10-15: AI, Semiconductors, Fintech, Sports, etc.)
- [ ] **DOM-02**: Each curated domain maps to a validated set of stock tickers
- [ ] **DOM-03**: User can create custom domains with user-selected stock tickers
- [ ] **DOM-04**: App validates stock tickers against Yahoo Finance before accepting them

### Dashboard UI

- [ ] **UI-01**: User sees a responsive dashboard with selected domains and their top 5 stocks
- [ ] **UI-02**: User can click a stock to see its full score breakdown
- [ ] **UI-03**: App shows loading/skeleton states during data refresh
- [ ] **UI-04**: App shows "Market Closed" banner with last close data outside trading hours
- [ ] **UI-05**: Dashboard works on desktop and mobile (responsive fintech style)

### Authentication

- [ ] **AUTH-01**: User can register with email and password
- [ ] **AUTH-02**: User can log in and receive a JWT token
- [ ] **AUTH-03**: User session persists across browser refresh
- [ ] **AUTH-04**: User's domain selections are saved and restored on login

### Historical Tracking

- [ ] **HIST-01**: App stores daily score snapshots for all ranked stocks
- [ ] **HIST-02**: User can view a stock's score history over time (chart)
- [ ] **HIST-03**: App shows score trend indicators (rising/falling) on the dashboard

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Notifications

- **NOTF-01**: User receives alerts when a stock enters/exits top 5
- **NOTF-02**: User receives daily digest email with best picks

### Advanced Features

- **ADV-01**: User can compare 2 stocks side-by-side
- **ADV-02**: User can configure algorithm weights (advanced mode)
- **ADV-03**: App supports additional data sources beyond Yahoo Finance

## Out of Scope

| Feature | Reason |
|---------|--------|
| ML/AI predictions | Contradicts core value of explainable math |
| Social sentiment analysis | Noisy signal, API costs, out of scope per PROJECT.md |
| Real-time streaming | 5-min polling sufficient, massive complexity |
| Portfolio tracking | Different product, liability concerns |
| Trading execution | Recommendation only per PROJECT.md |
| Backtesting | Survivorship bias risk, complex to do correctly |
| Price alerts | Requires persistent connections, defer to v2+ |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | Phase 1 | Pending |
| DATA-02 | Phase 1 | Pending |
| DATA-03 | Phase 1 | Pending |
| DATA-04 | Phase 1 | Pending |
| DATA-05 | Phase 1 | Pending |
| ALGO-01 | Phase 2 | Pending |
| ALGO-02 | Phase 2 | Pending |
| ALGO-03 | Phase 2 | Pending |
| ALGO-04 | Phase 2 | Pending |
| ALGO-05 | Phase 2 | Pending |
| ALGO-06 | Phase 2 | Pending |
| DOM-01 | Phase 3 | Pending |
| DOM-02 | Phase 3 | Pending |
| DOM-03 | Phase 5 | Pending |
| DOM-04 | Phase 5 | Pending |
| UI-01 | Phase 3 | Pending |
| UI-02 | Phase 3 | Pending |
| UI-03 | Phase 3 | Pending |
| UI-04 | Phase 3 | Pending |
| UI-05 | Phase 3 | Pending |
| AUTH-01 | Phase 4 | Pending |
| AUTH-02 | Phase 4 | Pending |
| AUTH-03 | Phase 4 | Pending |
| AUTH-04 | Phase 4 | Pending |
| HIST-01 | Phase 5 | Pending |
| HIST-02 | Phase 5 | Pending |
| HIST-03 | Phase 5 | Pending |

**Coverage:**
- v1.0 requirements: 27 total
- Mapped to phases: 27 ✓
- Unmapped: 0

---
*Requirements defined: 2026-02-17*
*Last updated: 2026-02-17 after initial definition*
