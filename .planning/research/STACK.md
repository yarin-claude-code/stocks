# Stack Research

**Domain:** Stock ranking / fintech
**Researched:** 2026-02-17
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.11+ | Backend language | Best ecosystem for financial math (numpy, pandas), FastAPI performance |
| FastAPI | 0.115+ | API framework | Async support for concurrent Yahoo Finance requests, auto OpenAPI docs, fast |
| React | 18+ | Frontend | User preference, huge ecosystem, component model fits dashboard UI |
| Vite | 5+ | Frontend build tool | Fast dev server, modern defaults, better DX than CRA |
| SQLite | 3.40+ | Database | Zero config, sufficient for single-VPS deployment, WAL mode handles concurrent reads |
| Node.js | 20 LTS | Frontend tooling | Required for React/Vite build pipeline |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| yfinance | 0.2.36+ | Yahoo Finance data | All stock data fetching — wraps Yahoo Finance API cleanly |
| pandas | 2.2+ | Data manipulation | Score calculation, normalization, time series handling |
| numpy | 1.26+ | Numerical computation | Algorithm math, statistical functions |
| SQLAlchemy | 2.0+ | ORM | Database models, migrations with Alembic |
| Alembic | 1.13+ | DB migrations | Schema versioning |
| APScheduler | 3.10+ | Task scheduling | 5-minute data fetch polling |
| python-jose | 3.3+ | JWT tokens | Auth token generation/validation |
| passlib[bcrypt] | 1.7+ | Password hashing | Secure password storage |
| pydantic | 2.6+ | Data validation | Request/response models (comes with FastAPI) |
| httpx | 0.27+ | HTTP client | Async requests if yfinance needs supplementing |
| axios | 1.7+ | HTTP client (frontend) | API calls from React |
| recharts | 2.12+ | Charts (frontend) | Stock score visualization, sparklines |
| tailwindcss | 3.4+ | CSS framework | Responsive fintech-style UI quickly |
| zustand | 4.5+ | State management | Lightweight, simpler than Redux for this scale |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| uvicorn | ASGI server | Dev + production server for FastAPI |
| pytest | Testing | Backend tests |
| ruff | Linting/formatting | Fast Python linter, replaces flake8+black |
| TypeScript | Type safety | Frontend type checking |

## Installation

```bash
# Backend
pip install fastapi uvicorn[standard] yfinance pandas numpy sqlalchemy alembic apscheduler python-jose[cryptography] passlib[bcrypt] httpx ruff pytest

# Frontend
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install axios recharts zustand
npm install -D tailwindcss postcss autoprefixer @types/node
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| SQLite | PostgreSQL | If expecting >100 concurrent users or need full-text search |
| yfinance | Yahoo Finance API direct | If yfinance breaks (it scrapes, can be fragile) |
| FastAPI | Flask | If team is more familiar, but FastAPI is strictly better here |
| APScheduler | Celery | If need distributed task queue — overkill for single VPS |
| zustand | Redux Toolkit | If state becomes very complex with many slices |
| recharts | Chart.js | If need more chart types, but recharts has better React integration |
| Tailwind | Material UI | If want pre-built components, but Tailwind is more flexible for custom fintech look |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Create React App | Deprecated, slow, no longer maintained | Vite |
| Django | Over-engineered for this scope, slower for API-only | FastAPI |
| MongoDB | Relational data (stocks, scores, users) fits SQL better | SQLite/PostgreSQL |
| Celery + Redis | Overkill for a single scheduled task on one VPS | APScheduler |
| pandas-datareader | Deprecated Yahoo Finance support | yfinance |
| alpha_vantage | Requires API key, rate limits more restrictive | yfinance |

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| FastAPI 0.115+ | Pydantic 2.x | FastAPI fully supports Pydantic v2 |
| SQLAlchemy 2.0+ | Alembic 1.13+ | Use 2.0-style queries |
| yfinance 0.2.36+ | pandas 2.x | Returns pandas DataFrames |

## Sources

- yfinance PyPI documentation
- FastAPI official docs
- Vite + React setup guides
- Domain expertise in fintech stack patterns

---
*Stack research for: Stock ranking / fintech*
*Researched: 2026-02-17*
