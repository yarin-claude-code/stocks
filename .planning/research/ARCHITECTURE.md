# Architecture Research

**Domain:** Stock ranking / fintech
**Researched:** 2026-02-17
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ Dashboard │  │ Domain   │  │ Auth     │               │
│  │ View     │  │ Selector │  │ Pages    │               │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘               │
│       └──────────────┴─────────────┘                     │
│                      │ REST API (axios)                   │
├──────────────────────┼───────────────────────────────────┤
│              FastAPI Backend                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ API      │  │ Ranking  │  │ Auth     │               │
│  │ Routes   │  │ Engine   │  │ Module   │               │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘               │
│       │              │              │                     │
│  ┌────┴──────────────┴──────────────┴─────┐              │
│  │         Data Service Layer              │              │
│  └────────────────┬────────────────────────┘              │
├───────────────────┼──────────────────────────────────────┤
│  ┌────────────────┴────────────────────────┐              │
│  │         SQLite Database                  │              │
│  │  stocks | scores | users | domains       │              │
│  └─────────────────────────────────────────┘              │
├──────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────┐              │
│  │     APScheduler (5-min polling)          │              │
│  │     → yfinance fetch → process → store   │              │
│  └─────────────────────────────────────────┘              │
└──────────────────────────────────────────────────────────┘
         ↕ Yahoo Finance (external, yfinance library)
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| API Routes | HTTP endpoints, request validation | FastAPI routers, Pydantic models |
| Ranking Engine | Score calculation, normalization, weighting | Pure Python module with numpy/pandas |
| Auth Module | JWT tokens, password hashing, session management | python-jose + passlib |
| Data Service | Database access, caching, data transformation | SQLAlchemy repositories |
| Scheduler | Periodic data fetching, score recalculation | APScheduler BackgroundScheduler |
| Dashboard View | Score display, domain selection, charts | React components + recharts |

## Recommended Project Structure

```
project-root/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app, startup events, scheduler
│   │   ├── config.py            # Settings (env vars, constants)
│   │   ├── database.py          # SQLAlchemy engine, session
│   │   ├── models/
│   │   │   ├── stock.py         # Stock, StockPrice, StockScore models
│   │   │   ├── user.py          # User model
│   │   │   └── domain.py        # Domain, DomainStock mapping
│   │   ├── routers/
│   │   │   ├── rankings.py      # GET /rankings, /rankings/{domain}
│   │   │   ├── domains.py       # GET/POST /domains
│   │   │   └── auth.py          # POST /login, /register
│   │   ├── services/
│   │   │   ├── data_fetcher.py  # Yahoo Finance fetching + caching
│   │   │   ├── ranking_engine.py # THE algorithm — scoring, normalization
│   │   │   └── auth_service.py  # JWT, password handling
│   │   └── schemas/
│   │       ├── rankings.py      # Response models
│   │       └── auth.py          # Auth request/response models
│   ├── alembic/                 # DB migrations
│   ├── tests/
│   ├── requirements.txt
│   └── alembic.ini
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.tsx     # Main view
│   │   │   ├── DomainSelector.tsx
│   │   │   ├── StockCard.tsx     # Individual stock score display
│   │   │   ├── ScoreBreakdown.tsx # Factor contribution chart
│   │   │   └── BestOverall.tsx   # Hero "Best Investment Today"
│   │   ├── stores/
│   │   │   └── appStore.ts      # zustand store
│   │   ├── api/
│   │   │   └── client.ts        # axios instance + API functions
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── tailwind.config.js
├── .planning/                   # GSD planning artifacts
└── README.md
```

### Structure Rationale

- **backend/app/**: Flat-ish structure — small app doesn't need deep nesting
- **models/**: SQLAlchemy models separate from Pydantic schemas
- **services/**: Business logic isolated from routes — ranking_engine.py is the core
- **routers/**: One router per domain area
- **frontend/components/**: Feature-oriented, not atomic design (overkill for this size)

## Architectural Patterns

### Pattern 1: Scheduled Data Pipeline

**What:** Background scheduler fetches data, processes it, stores results. API serves cached results.
**When to use:** When data source has rate limits and freshness requirements are relaxed (5-min ok).
**Trade-offs:** Simple, no real-time. Slight staleness (up to 5 min) is acceptable.

```python
# Scheduler runs every 5 minutes
async def fetch_and_rank():
    raw_data = await data_fetcher.fetch_all_stocks()
    scores = ranking_engine.calculate_scores(raw_data)
    await db.store_scores(scores)
```

### Pattern 2: Service Layer Pattern

**What:** Routes delegate to services, services contain business logic, services use repositories for data.
**When to use:** When business logic (ranking algorithm) is the core value and needs to be testable independently.
**Trade-offs:** Slightly more files, but algorithm is isolated and testable.

### Pattern 3: Precomputed Rankings

**What:** Rankings computed on fetch, not on request. API serves precomputed results.
**When to use:** When ranking is expensive and data changes infrequently (every 5 min).
**Trade-offs:** API responses are instant. Rankings are at most 5 min stale.

## Data Flow

### Fetch-Rank-Serve Flow (Core)

```
[APScheduler: every 5 min]
    ↓
[data_fetcher.py] → yfinance.download() → raw price/volume/ratio data
    ↓
[ranking_engine.py] → normalize → weight → composite score per stock
    ↓
[database] → store scores + raw data snapshot
    ↓
[API request] → query precomputed scores → return top 5 per domain
```

### User Request Flow

```
[React] → GET /api/rankings?domains=AI,Semiconductors
    ↓
[FastAPI router] → query latest scores for requested domains
    ↓
[Database] → SELECT scores WHERE domain IN (...) ORDER BY score DESC LIMIT 5
    ↓
[Response] → { domain: "AI", stocks: [{ticker, name, score, breakdown, ...}] }
```

### Key Data Flows

1. **Data ingestion:** Scheduler → yfinance → normalize → store (every 5 min)
2. **Score serving:** React → FastAPI → SQLite → precomputed scores → JSON response
3. **Auth flow:** React → POST /login → JWT issued → stored in localStorage → sent in headers

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 1-50 users | SQLite + single process — current design is sufficient |
| 50-500 users | Add SQLite WAL mode, consider uvicorn workers (2-4) |
| 500+ users | Migrate to PostgreSQL, add nginx reverse proxy, consider Redis cache |

### Scaling Priorities

1. **First bottleneck:** Yahoo Finance rate limiting — solved by caching (fetch once, serve many)
2. **Second bottleneck:** SQLite write contention — WAL mode handles this up to ~500 concurrent readers

## Anti-Patterns

### Anti-Pattern 1: Fetching on Every Request

**What people do:** Call Yahoo Finance on each API request
**Why it's wrong:** Rate limited instantly, 2-3 second response times, unreliable
**Do this instead:** Precompute on schedule, serve from cache/DB

### Anti-Pattern 2: Monolithic Ranking Function

**What people do:** One giant function that fetches, processes, normalizes, and ranks
**Why it's wrong:** Untestable, can't debug individual factors, hard to tune weights
**Do this instead:** Separate fetch → normalize → score → rank into distinct functions

### Anti-Pattern 3: Frontend State as Source of Truth

**What people do:** Store domain selections and rankings in React state only
**Why it's wrong:** Lost on refresh, can't share, no persistence
**Do this instead:** Backend stores preferences (for auth users), frontend caches for display

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Yahoo Finance | yfinance library, scheduled polling | Rate limit: ~2000 requests/hour, batch downloads reduce calls |
| Hostinger VPS | systemd service + nginx reverse proxy | Need to configure CORS, SSL (Let's Encrypt) |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Frontend ↔ Backend | REST JSON API | CORS configured, /api prefix |
| Backend ↔ Database | SQLAlchemy ORM | Async sessions for FastAPI |
| Scheduler ↔ Services | Direct function calls (same process) | No message queue needed |

## Sources

- FastAPI project structure best practices
- yfinance batch download patterns
- SQLite performance characteristics for read-heavy workloads
- Fintech dashboard architecture patterns

---
*Architecture research for: Stock ranking / fintech*
*Researched: 2026-02-17*
