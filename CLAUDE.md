# Smart Stock Ranker — Claude Context

## Project Overview

Full-stack stock ranking app. Python/FastAPI backend + React frontend (Phase 3+). Core product is the **quantitative ranking algorithm** — math correctness > UI polish.

**Stack:** FastAPI + SQLAlchemy 2.0 (async) + Supabase Postgres + APScheduler + yfinance + Alembic + pytest

**Current milestone:** v1.0 Smart Stock Ranker
**Current phase:** 02 — Ranking Algorithm
**Planning docs:** `.planning/` directory (ROADMAP.md, STATE.md, PROJECT.md)

---

## Repository Layout

```
investment-project/
├── backend/                  # FastAPI app — the entire current focus
│   ├── app/
│   │   ├── config.py         # Settings via pydantic-settings (.env loaded here)
│   │   ├── database.py       # Async engine (asyncpg), Base, get_db(), seed_db()
│   │   ├── main.py           # FastAPI app + lifespan (create_all, seed, scheduler)
│   │   ├── scheduler.py      # APScheduler BackgroundScheduler + sync engine (psycopg2)
│   │   ├── seed.py           # Idempotent domain/stock seeding
│   │   ├── models/
│   │   │   ├── stock.py      # Domain, Stock (SQLAlchemy Mapped syntax)
│   │   │   └── score_snapshot.py  # ScoreSnapshot (ticker, close_price, volume, fetched_at)
│   │   ├── routers/
│   │   │   └── health.py     # GET /api/health — last_fetched timestamp
│   │   └── services/
│   │       └── data_fetcher.py    # yfinance batch fetch, validate_ticker_data()
│   ├── tests/
│   │   └── test_data_fetcher.py
│   ├── alembic/              # Migrations targeting Supabase Postgres
│   │   ├── env.py
│   │   └── versions/81cb55ab1baf_initial_schema.py
│   ├── alembic.ini
│   └── requirements.txt
└── .planning/                # GSD planning docs — do not modify unless doing planning work
```

Frontend not yet created (Phase 3).

---

## Environment

**Backend `.env`** lives at `backend/.env` (gitignored). Required vars:

```
DATABASE_URL=postgresql+asyncpg://...@db.<project>.supabase.co:5432/postgres
FETCH_INTERVAL_MINUTES=5
```

- Port **5432** (direct Postgres) — NOT 6543 (pgbouncer). SQLAlchemy session mode requires direct connection.
- `sync_database_url` is derived automatically from `database_url` by replacing `asyncpg` → `psycopg2` in `Settings`.

**Run the backend:**

```bash
cd backend
uvicorn app.main:app --reload
```

**Run tests:**

```bash
cd backend
python -m pytest tests/ -v
```

**Run Alembic migrations:**

```bash
cd backend
alembic upgrade head
```

---

## Architecture Decisions (critical — do not change without good reason)

| Decision | Why |
|----------|-----|
| **Two-engine pattern** | Async engine (asyncpg) for FastAPI; sync engine (psycopg2) for APScheduler thread. yfinance is sync — AsyncIOScheduler would block the event loop. |
| **BackgroundScheduler (not AsyncIOScheduler)** | yfinance is synchronous; running it in the async event loop would block all requests. |
| **SQLAlchemy 2.0 `Mapped[T]` / `mapped_column`** | Type-safe, not legacy `Column`. All models use this. |
| **FastAPI `@asynccontextmanager` lifespan** | Not deprecated `@app.on_event`. Handles startup/shutdown of scheduler + DB engine. |
| **Single `yf.download()` batch call** | Avoids per-ticker rate limits. Returns multi-ticker DataFrame sliced per ticker. |
| **`math.isnan()` for validation** | Pure stdlib, no pandas dependency in `validate_ticker_data()`. |
| **`fetch_all_stocks` silent fallback** | Returns `{}` on ANY exception. Caller gets last-known-good data from DB. Never raises. |
| **Alembic URL injected via `config.set_main_option`** | configparser `%(VAR)s` interpolation cannot read env vars. URL injected programmatically after `load_dotenv()` in `env.py`. |
| **Supabase direct port 5432** | pgbouncer (6543) incompatible with SQLAlchemy session mode. |
| **`scheduler.shutdown(wait=False)`** | Prevents blocking app shutdown when a fetch is in progress. |

---

## Coding Conventions

- **Pure modules are pure:** `ranking_engine.py` (Phase 2) must NOT import `app.database`, `app.models`, or `yfinance`. Only `dataclasses`, `typing`, `numpy`.
- **ddof=0 everywhere:** Population std (not sample std) for Z-score normalization.
- **No magic numbers:** All factor weights in `ranking_engine.py` are named module-level constants.
- **Idempotent seeds:** `seed_db()` uses select-then-insert — safe to re-run.
- **Test from `backend/` dir:** `cd backend && python -m pytest tests/ -v` — import paths assume working dir is `backend/`.
- **SQLAlchemy 2.0 `Mapped[T]` / `mapped_column`** everywhere — not legacy `Column`.

---

## Backend — Import Paths & Test Patterns

Tests import using `app.*` prefix (working dir is `backend/`):

```python
from app.services.ranking_engine import rank_domain, normalize_factor, StockScore, FactorScore
from app.services.data_fetcher import fetch_all_stocks
from app.config import settings
from app.database import get_db
```

Sync tests (e.g. `ranking_engine.py`) — plain `def test_*`, no async setup needed.

Async tests — use `pytest-asyncio`:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
    assert response.status_code == 200
```

## Backend — Session Rules

- **Async sessions** (`async_session_maker`) — FastAPI route handlers only
- **Sync sessions** (`Session(_sync_engine)`) — scheduler thread only
- Never mix: no async session inside scheduler, no sync engine in route handlers

---

## Phase 2 — Ranking Algorithm (current work)

**Files to create:**
- `backend/app/services/ranking_engine.py` — pure scoring engine
- `backend/tests/test_ranking_engine.py` — 6 TDD test cases

**Factor weights (must sum to 1.0):**

```python
WEIGHT_MOMENTUM          = 0.30   # 5-day price return
WEIGHT_VOLUME_CHANGE     = 0.20   # 5-day volume change
WEIGHT_VOLATILITY        = 0.20   # 21-day rolling std (INVERTED before passing in)
WEIGHT_RELATIVE_STRENGTH = 0.15   # stock return minus domain median
WEIGHT_FINANCIAL_RATIO   = 0.15   # trailingPE (INVERTED before passing in)
```

**Key behaviors:**
- `normalize_factor()`: cap ±3σ → Z-score; std==0 → all 0.0; fewer than 2 non-None → all None
- `compute_composite()`: exclude None factors; proportionally reweight remaining to sum to 1.0
- `scale_to_0_100()`: min-max within peer group; if max==min → all 50.0
- `rank_domain()`: single stock → score=50.0, rank=1; empty → `{}`
- `financial_ratio` None is the **normal case** (yfinance trailingPE often missing) — reweighting fires regularly

See `.planning/phases/02-ranking-algorithm/02-01-PLAN.md` for full spec.

---

## What NOT to Do

- Do not add ML/neural networks — explainable math only
- Do not add websocket streaming — 5-min polling is sufficient
- Do not use `AsyncIOScheduler` for yfinance jobs (it's sync)
- Do not use `scipy` — only `numpy` available in requirements
- Do not use `ddof=1` (sample std) — use `ddof=0` (population std)
- Do not import I/O dependencies inside `ranking_engine.py`
- Do not change Supabase port to 6543 (pgbouncer) — use 5432
