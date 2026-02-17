# Project Research Summary

**Project:** Stock Ranking Platform
**Domain:** Fintech / Stock Screening
**Researched:** 2026-02-17
**Confidence:** HIGH

## Executive Summary

This is a stock ranking and screening platform that helps retail investors identify top investment opportunities through domain-based organization (AI, Sports, Semiconductors) rather than traditional sector classification. The expert consensus is clear: build this as a precomputed ranking system with scheduled data fetching, not a real-time streaming platform. The architecture centers on a FastAPI backend polling Yahoo Finance every 5 minutes, calculating weighted composite scores using normalized quantitative factors, and serving cached results through a React dashboard.

The recommended stack is Python (FastAPI) for backend with yfinance for data, React (Vite) for frontend, and SQLite for persistence. This combination provides the right balance of financial data ecosystem maturity (numpy/pandas), API performance (async FastAPI), and deployment simplicity (SQLite on single VPS). The core differentiator is making ranking algorithms transparent and explainable—showing users the mathematical breakdown of why each stock received its score, not just presenting opaque numbers.

Key risks center on Yahoo Finance reliability (it's scraped, not an official API) and algorithm credibility (arbitrary weights destroy user trust). Mitigation requires aggressive caching with graceful degradation when Yahoo Finance fails, and documenting clear rationale for every scoring factor weight. Score normalization must use z-scores within peer groups to avoid one factor dominating all rankings. The product succeeds if users trust the algorithm enough to act on recommendations—transparency is non-negotiable.

## Key Findings

### Recommended Stack

Modern fintech tools optimized for quantitative data processing and API performance. Python dominates financial data manipulation (pandas, numpy) while FastAPI provides async capabilities needed for concurrent data fetching. React + Vite ensures fast frontend development with TypeScript safety. SQLite is sufficient for single-VPS deployment given read-heavy workload patterns.

**Core technologies:**
- **Python 3.11+ with FastAPI 0.115+**: Backend language and API framework — async support for concurrent Yahoo Finance requests, automatic OpenAPI documentation, best-in-class financial math ecosystem (pandas, numpy)
- **React 18+ with Vite 5+**: Frontend framework and build tool — component model fits dashboard UI, fast dev server, modern defaults superior to Create React App
- **yfinance 0.2.36+ with pandas 2.2+**: Yahoo Finance data fetching — wraps Yahoo Finance API cleanly, returns pandas DataFrames ready for algorithm processing
- **SQLite 3.40+ with SQLAlchemy 2.0+**: Database and ORM — zero-config deployment, WAL mode handles concurrent reads, sufficient for <500 users
- **APScheduler 3.10+**: Task scheduling — handles 5-minute polling cycles without Celery/Redis overhead
- **Tailwind CSS 3.4+ with recharts 2.12+**: Styling and visualization — responsive fintech UI quickly, stock score charts and sparklines

**Critical version notes:**
- FastAPI 0.115+ requires Pydantic 2.x (breaking change from v1)
- SQLAlchemy 2.0+ uses new query syntax (not 1.x style)
- yfinance 0.2.36+ compatible with pandas 2.x

**What to avoid:**
- Create React App (deprecated, use Vite)
- Django (over-engineered, slower for API-only)
- Celery + Redis (overkill for single scheduled task)
- Real-time WebSockets (5-minute polling sufficient)

### Expected Features

Domain-based stock screening with transparent algorithmic ranking. Users expect clear explanations of scores (table stakes), while the domain organization model and "Best Overall Investment Today" single pick provide competitive differentiation. Anti-features include real-time data (unnecessary complexity), ML predictions (unexplainable), and portfolio tracking (scope creep).

**Must have (table stakes):**
- **Stock scores with clear ranking** — weighted composite score normalized 0-100, users need quantitative clarity
- **Domain/sector filtering** — curated lists (AI, Sports, Semiconductors) + custom, users want stocks matching their interests
- **Top N display per category** — top 5 per domain, standard screener pattern
- **Score breakdown/explanation** — show each factor's contribution, users distrust black-box algorithms
- **Data freshness indicator** — "Last updated X min ago" timestamp, users need to know staleness
- **Mobile-responsive layout** — majority of retail investors check on mobile
- **Basic auth with saved preferences** — return users expect domain selections to persist

**Should have (competitive differentiators):**
- **"Best Overall Investment Today"** — single actionable pick across all domains, most screeners overwhelm with data
- **Domain-based organization** — mapping stocks to interest domains (AI, Sports) more intuitive than GICS sectors
- **Mathematical score explanation** — formula breakdown showing weighted factors, transparency builds trust
- **Historical score tracking** — see rank changes over time, identify rising/falling stocks
- **Custom domain creation** — user-defined stock groupings with ticker validation

**Defer (v2+):**
- **Real-time streaming prices** — 5-minute polling sufficient for ranking use case, real-time adds massive complexity
- **ML/AI predictions** — unexplainable, unreliable, contradicts core transparency value
- **Social sentiment integration** — noisy signal, API costs, manipulation-prone
- **Portfolio tracking** — different product, liability concerns, scope creep
- **Price alerts** — requires persistent connections, notification infrastructure
- **Backtesting** — survivorship bias and look-ahead bias difficult to handle correctly

### Architecture Approach

Scheduled data pipeline with precomputed rankings served through API. APScheduler runs every 5 minutes to fetch Yahoo Finance data via yfinance (batch download), calculate scores using weighted normalization in ranking_engine.py, and store results in SQLite. API requests serve precomputed scores—no computation happens on request path. This pattern optimizes for Yahoo Finance rate limits (fetch once, serve many) and makes API responses instant.

**Major components:**
1. **Data Fetcher (services/data_fetcher.py)** — Yahoo Finance polling with yfinance batch downloads, error handling for empty responses, caching layer to avoid rate limits
2. **Ranking Engine (services/ranking_engine.py)** — THE core algorithm: z-score normalization per factor, outlier capping, weighted composite calculation, peer group ranking
3. **Scheduler (APScheduler in main.py)** — 5-minute polling cycle triggering fetch → calculate → store pipeline, runs in background of FastAPI process
4. **API Routes (routers/)** — FastAPI endpoints serving precomputed rankings, domain management, authentication with JWT
5. **React Dashboard (frontend/)** — Domain selector, top 5 stock cards per domain, score breakdown charts, "Best Overall" hero section

**Key patterns:**
- **Precomputed rankings pattern:** Rankings calculated on schedule, not on request — trades 5-min staleness for instant API responses
- **Service layer pattern:** Routes delegate to services, services contain algorithm logic, isolated for testing
- **Batch data fetching:** Single yfinance.download() call with multiple tickers reduces rate limit hits from 200+ to 1 per cycle

**Data flow:**
```
[APScheduler: every 5 min] → [yfinance batch fetch] → [ranking_engine normalization]
    → [SQLite storage] → [API request] → [serve precomputed scores]
```

### Critical Pitfalls

Top risks identified with prevention strategies derived from domain expertise and yfinance failure patterns.

1. **Yahoo Finance rate limiting and breakage** — yfinance scrapes Yahoo (not official API), HTML changes break it regularly, rate limits at ~2000 req/hour. **Avoid by:** batch downloading all tickers in one yf.download() call, caching aggressively (5-min cycle serves many requests), validating for NaN/empty DataFrames, fallback to last known good data when fetch fails. **Phase 1 critical.**

2. **Naive score normalization** — factors have different scales (price % vs volume millions vs P/E ratios), raw values can't be weighted meaningfully. **Avoid by:** z-score normalization per factor (subtract mean, divide by std dev), cap outliers at ±3 standard deviations, normalize within peer group (same domain) not globally, test edge cases (1 stock in domain, extreme values). **Phase 2 critical.**

3. **Survivorship bias in domain stock lists** — curated lists only include currently-successful companies, making historical analysis misleading. **Avoid by:** accepting this for live ranking (rank what exists today), noting historical scores are for currently-listed stocks only, avoiding backtesting claims, re-validating tickers periodically (META was FB). **Phase 1 and historical features.**

4. **Stale data served as fresh** — scheduler fails silently, users see hours-old rankings without warning, make decisions on outdated data. **Avoid by:** always display "last updated" timestamp, health check endpoint verifying recent fetch, warning banner if data >15 minutes old, prominent logging of fetch failures. **Phase 1 + UI phase.**

5. **Algorithm weights that can't be justified** — arbitrary weight choices (30% momentum, 20% volume) produce questionable rankings, developer can't explain rationale. **Avoid by:** documenting reasoning for each weight, starting with equal weights then adjusting with clear justification, showing factor contributions in UI so users see what drives scores, considering configurable weights (advanced). **Phase 2 critical.**

**Additional technical debt acceptable at MVP:**
- Hardcoded stock-to-domain mappings acceptable for v1, move to DB in v1.1
- SQLite acceptable for <500 users, migrate to PostgreSQL if scaling
- JWT in localStorage acceptable for read-only recommendation app (no financial transactions)
- Never skip test coverage for ranking algorithm — algorithm IS the product

## Implications for Roadmap

Based on research, suggested phase structure prioritizes data reliability and algorithm transparency before adding user-facing features.

### Phase 1: Data Pipeline Foundation
**Rationale:** Can't rank stocks without reliable data. Yahoo Finance rate limiting is the #1 technical risk—must solve caching and error handling first. All features depend on this working.

**Delivers:**
- Functional yfinance integration with batch downloading
- SQLite database schema (stocks, scores, domains)
- APScheduler setup with 5-minute polling
- Error handling and graceful degradation
- "Last updated" timestamp tracking

**Addresses features:**
- Data freshness indicator (table stakes)
- Foundation for all ranking features

**Avoids pitfalls:**
- Yahoo Finance rate limiting (batch fetch, caching)
- Stale data served as fresh (timestamp, health checks)
- Survivorship bias (ticker validation, periodic re-checks)

**Research needs:** Standard pattern, skip `/gsd:research-phase`

---

### Phase 2: Ranking Algorithm
**Rationale:** The algorithm IS the product. Must be correct, explainable, and tested before building UI. This is where competitive advantage lives—getting normalization and weights right is critical.

**Delivers:**
- Z-score normalization with outlier handling
- Weighted composite scoring with documented rationale
- Peer group ranking (within domains)
- Score breakdown data structure
- Comprehensive test suite for edge cases

**Uses stack:**
- pandas for data manipulation
- numpy for statistical functions
- pytest for algorithm validation

**Implements architecture:**
- services/ranking_engine.py as isolated, testable module
- Clear separation: normalize → weight → rank

**Avoids pitfalls:**
- Naive normalization (z-scores, outlier caps, peer groups)
- Unjustified weights (document rationale, show contributions)

**Research needs:** Might benefit from `/gsd:research-phase` focused on quantitative finance normalization best practices and factor weight selection methods

---

### Phase 3: Basic API & Dashboard
**Rationale:** With data pipeline and algorithm solid, build minimal UI to prove value. Focus on top 5 per domain and "Best Overall" pick—the differentiators that set this apart from Finviz.

**Delivers:**
- FastAPI routes for /rankings, /rankings/{domain}
- React dashboard with domain selector
- Top 5 stock cards per domain
- "Best Overall Investment Today" hero section
- Score breakdown visualization (recharts)
- Mobile-responsive layout (Tailwind)

**Addresses features:**
- Stock scores with clear ranking (table stakes)
- Domain filtering (table stakes)
- Top N display (table stakes)
- Score breakdown (table stakes)
- Mobile-responsive (table stakes)
- Best Overall pick (differentiator)
- Domain-based organization (differentiator)
- Mathematical explanation (differentiator)

**Implements architecture:**
- routers/rankings.py
- React components (Dashboard, DomainSelector, StockCard, BestOverall)
- CORS configuration

**Research needs:** Standard React + FastAPI integration, skip `/gsd:research-phase`

---

### Phase 4: Authentication & Personalization
**Rationale:** Once core value proven, add persistence. Auth enables saved domain preferences and sets foundation for custom domains.

**Delivers:**
- JWT authentication (python-jose, passlib)
- User registration and login
- Saved domain selections
- User preferences persistence

**Addresses features:**
- Basic auth with saved preferences (table stakes)

**Uses stack:**
- python-jose for JWT tokens
- passlib[bcrypt] for password hashing
- SQLAlchemy User model

**Implements architecture:**
- routers/auth.py
- services/auth_service.py
- JWT in localStorage (frontend)

**Research needs:** Standard pattern, skip `/gsd:research-phase`

---

### Phase 5: Historical Tracking & Custom Domains
**Rationale:** With auth in place, add features that require user context. Historical tracking shows score evolution, custom domains let users create their own categories.

**Delivers:**
- Daily score snapshots
- Historical score trend visualization
- Custom domain creation with ticker validation
- Score trend indicators (rising/falling)

**Addresses features:**
- Historical score tracking (differentiator)
- Custom domain creation (differentiator)

**Implements architecture:**
- Daily score snapshot storage
- Time series queries
- User-owned domain mappings

**Avoids pitfalls:**
- Survivorship bias (note limitation in historical view)
- Timezone handling (all timestamps UTC)

**Research needs:** Might benefit from `/gsd:research-phase` focused on time series storage patterns in SQLite and efficient historical data visualization

---

### Phase Ordering Rationale

**Dependency-driven ordering:**
- Phase 1 (data) must come first—nothing works without reliable Yahoo Finance integration
- Phase 2 (algorithm) must precede UI—can't display rankings without calculation logic
- Phase 4 (auth) must precede Phase 5 (custom domains)—need user context for personalization

**Risk-mitigation ordering:**
- Address Yahoo Finance rate limiting (highest risk) in Phase 1
- Address algorithm credibility (core value) in Phase 2 before building UI
- Defer custom domains until core features validated

**Value delivery ordering:**
- Phase 3 delivers MVP: functional dashboard showing ranked stocks
- Phase 4 adds stickiness: users can save preferences
- Phase 5 adds depth: historical trends and customization

**Architecture alignment:**
- Phases map to service layer boundaries (data_fetcher → ranking_engine → API routes → auth_service)
- Each phase delivers a testable, isolated module

### Research Flags

**Phases likely needing deeper research during planning:**
- **Phase 2 (Ranking Algorithm):** Quantitative finance normalization best practices are nuanced—benefit from targeted research on factor selection, z-score vs percentile normalization trade-offs, and weight selection methodologies used by Seeking Alpha, Zacks, etc.
- **Phase 5 (Historical Tracking):** Time series storage in SQLite and efficient querying patterns for trend visualization—research optimal schema (wide vs narrow tables, indexing strategies).

**Phases with standard patterns (skip research-phase):**
- **Phase 1 (Data Pipeline):** yfinance usage well-documented, APScheduler setup standard
- **Phase 3 (API & Dashboard):** FastAPI + React integration thoroughly documented
- **Phase 4 (Authentication):** JWT auth is solved problem, FastAPI docs cover it

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | FastAPI + React + yfinance is proven combination for fintech, version compatibility verified, clear alternatives identified |
| Features | HIGH | Feature landscape well-understood from competitor analysis (Finviz, Stock Rover), table stakes vs differentiators clear, anti-features identified from domain expertise |
| Architecture | HIGH | Scheduled data pipeline with precomputed rankings is standard pattern for rate-limited external APIs, service layer boundaries well-defined, scaling characteristics understood |
| Pitfalls | HIGH | Top 5 pitfalls derived from yfinance GitHub issues, quantitative finance best practices, and fintech UX research—specific prevention strategies documented with phase mapping |

**Overall confidence:** HIGH

Research is comprehensive and actionable. Stack choices justified with clear rationale and version specifications. Feature prioritization backed by competitor analysis and user expectation patterns. Architecture follows proven fintech patterns for read-heavy workloads with rate-limited data sources. Pitfalls identified from real-world failure modes with concrete prevention strategies.

### Gaps to Address

Minor gaps that need attention during implementation but don't block roadmap creation:

- **Algorithm weight selection methodology:** Research suggests documenting rationale but doesn't prescribe specific weights. During Phase 2 planning, consider targeted research on factor importance in quant investing (momentum vs value vs growth) or start with equal weights and tune based on manual validation.

- **SQLite to PostgreSQL migration threshold:** Research identifies "<500 users" as SQLite limit but doesn't define migration process. During Phase 1 planning, document backup strategy and schema design to make migration easier if needed.

- **yfinance fallback strategy:** Research recommends fallback to last known good data when yfinance fails, but doesn't specify data retention policy. During Phase 1 planning, decide how long to serve stale data before showing error state (suggest 24 hours).

- **Custom domain ticker validation:** Research notes need for validation but doesn't specify approach. During Phase 5 planning, decide between: (a) validate against static list, (b) test-fetch from yfinance, (c) allow any ticker and handle errors later.

## Sources

### Primary (HIGH confidence)
- **yfinance PyPI documentation** — API patterns, batch download capabilities, pandas integration
- **FastAPI official documentation** — async patterns, Pydantic v2 compatibility, project structure best practices
- **Vite + React official guides** — setup, TypeScript integration, build optimization
- **SQLite official documentation** — WAL mode, concurrent read characteristics, scaling limits
- **pandas documentation** — DataFrame manipulation, statistical functions, time series handling

### Secondary (MEDIUM confidence)
- **yfinance GitHub issues** — rate limiting patterns, failure modes, community workarounds
- **Finviz.com feature analysis** — competitor feature set, UX patterns, sector vs domain organization
- **Stock Rover feature comparison** — scoring approaches, data freshness models, screening patterns
- **TradingView screener capabilities** — visualization approaches, mobile responsiveness patterns
- **Seeking Alpha quant ratings approach** — factor-based scoring, weight selection, transparency patterns

### Tertiary (domain expertise)
- **Fintech dashboard architecture patterns** — service layer design, precomputed vs on-demand trade-offs
- **Retail investor UX research patterns** — mobile usage, trust factors, explanation needs
- **Quantitative finance normalization best practices** — z-score vs percentile, outlier handling, peer group selection

---
*Research completed: 2026-02-17*
*Ready for roadmap: yes*
