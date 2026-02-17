# Phase 1: Data Pipeline Foundation - Research

**Researched:** 2026-02-17
**Domain:** Yahoo Finance data ingestion, SQLite persistence, APScheduler job scheduling, FastAPI project scaffolding
**Confidence:** HIGH

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DATA-01 | App fetches stock price/volume data from Yahoo Finance in batch every 5 minutes | yfinance `download()` batch API + APScheduler `IntervalTrigger(minutes=5)` |
| DATA-02 | App caches fetched data in database to avoid redundant API calls | SQLAlchemy 2.0 + aiosqlite write on each fetch cycle; API reads from DB, never calls yfinance directly |
| DATA-03 | App falls back to last-known-good data when Yahoo Finance fetch fails | Try/except around `yf.download()`, return latest row from `score_snapshots` table on failure |
| DATA-04 | App validates fetched data for completeness (no NaN, no empty results) | Post-download DataFrame validation: `df.empty`, `df.isnull().any()`, drop/flag bad tickers |
| DATA-05 | App displays "last updated" timestamp on all data views | Store `fetched_at` UTC timestamp on each row; expose via `/api/health` endpoint and in all ranking responses |
</phase_requirements>

---

## Summary

Phase 1 establishes the data ingestion backbone that all subsequent phases consume. The core pattern is straightforward: APScheduler fires every 5 minutes, `data_fetcher.py` calls `yf.download()` with the full ticker list in one batch request, validates the resulting DataFrame, persists it to SQLite via SQLAlchemy, and updates a "last fetched" timestamp. All API endpoints serve precomputed data from the database — they never touch yfinance directly.

yfinance released version 1.0 in December 2025 (current: 1.2.0 as of February 2026) with **no breaking changes** to the `download()` API from 0.2.x. The stack decision to use yfinance 0.2.36+ remains valid; pinning to `yfinance>=1.0` is preferable now. Rate limiting from Yahoo Finance is the primary reliability risk: 429 errors can appear with heavy polling. Mitigation is batching all tickers in a single `yf.download()` call per cycle (reduces requests from N to 1), plus exponential backoff retry logic and fallback to cached data.

APScheduler 3.x (current: 3.11.2) is the correct choice over 4.x — APScheduler 4.x remains in pre-release beta with breaking API changes and is not production-ready. For FastAPI integration, start the scheduler inside a `@asynccontextmanager` lifespan function using `BackgroundScheduler` (for sync jobs) or `AsyncIOScheduler` (for async jobs). The `@app.on_event` approach is deprecated; use `lifespan=` parameter instead.

**Primary recommendation:** Use `yf.download(tickers_list, period="1d", interval="1m", progress=False)` in a single batch call every 5 minutes, validate the DataFrame, upsert to SQLite via SQLAlchemy 2.0 (sync ORM with `run_in_executor` or aiosqlite for async), and expose a `/api/health` endpoint that returns last fetch timestamp and status.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| yfinance | >=1.0 (latest: 1.2.0) | Yahoo Finance batch price fetching | Wraps Yahoo Finance API, no key required, `download()` supports batch mode |
| SQLAlchemy | 2.0+ | ORM + query builder | Standard Python ORM, async support via aiosqlite, Alembic migrations |
| aiosqlite | 0.20+ | Async SQLite driver | Required for `create_async_engine` with SQLite in FastAPI async context |
| APScheduler | 3.10 / 3.11 | 5-minute polling scheduler | Battle-tested, clean FastAPI lifespan integration, simple interval jobs |
| FastAPI | 0.115+ | API framework + lifespan events | Lifespan `asynccontextmanager` for scheduler startup/shutdown |
| Alembic | 1.13+ | Database schema migrations | Works with SQLAlchemy 2.0 `DeclarativeBase`, manages SQLite schema evolution |
| pandas | 2.2+ | DataFrame handling for yfinance output | yfinance returns pandas DataFrames; needed for validation and transformation |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| uvicorn | 0.30+ | ASGI server | Dev and production server for FastAPI |
| pydantic | 2.x | Request/response schemas | Comes with FastAPI; use for API response models |
| python-dotenv | 1.0+ | Environment config | Load DATABASE_URL and settings from .env file |
| pytest | 8.x | Testing | Unit test `data_fetcher.py` validation logic |
| pytest-asyncio | 0.23+ | Async test support | Test async FastAPI routes and services |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| APScheduler 3.x | APScheduler 4.x | 4.x is still pre-release beta; API is breaking; use 3.x until 4.x stabilizes |
| APScheduler 3.x | Celery + Redis | Overkill for a single polling task on one VPS; no distributed queue needed |
| aiosqlite (async) | Sync SQLAlchemy + `run_in_threadpool` | Either is valid; async is cleaner but adds aiosqlite dependency |
| yfinance | Direct Yahoo Finance HTTP | yfinance handles auth headers, parsing, retries; re-implementing is wasteful |
| Alembic | `Base.metadata.create_all()` | `create_all()` is fine for Phase 1 only; add Alembic before schema changes are needed |

**Installation:**
```bash
pip install fastapi uvicorn[standard] yfinance pandas sqlalchemy aiosqlite alembic apscheduler python-dotenv pytest pytest-asyncio
```

---

## Architecture Patterns

### Recommended Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + lifespan (scheduler start/stop)
│   ├── config.py            # Settings via pydantic BaseSettings
│   ├── database.py          # create_async_engine, async_session_maker, Base
│   ├── models/
│   │   ├── __init__.py
│   │   ├── stock.py         # Stock model (ticker, name, domain)
│   │   ├── domain.py        # Domain model + stock-domain mapping
│   │   └── score_snapshot.py # ScoreSnapshot (fetched_at, raw prices, last known good)
│   ├── services/
│   │   └── data_fetcher.py  # yfinance batch fetch, validation, upsert to DB
│   ├── routers/
│   │   └── health.py        # GET /api/health — last fetch time, status
│   └── scheduler.py         # APScheduler setup, add_job for fetch_cycle
├── alembic/
├── alembic.ini
├── requirements.txt
└── tests/
    └── test_data_fetcher.py

frontend/                    # Scaffolding only in Phase 1
├── src/
│   ├── App.tsx
│   └── main.tsx
├── package.json
└── vite.config.ts
```

### Pattern 1: Lifespan-Managed Scheduler

**What:** Scheduler started/stopped inside FastAPI `lifespan` context manager, not deprecated `on_event`.
**When to use:** Always — `on_event` is deprecated in FastAPI 0.93+.

```python
# backend/app/main.py
# Source: FastAPI official docs — https://fastapi.tiangolo.com/advanced/events/
from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from app.scheduler import create_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = create_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
```

### Pattern 2: Batch yfinance Download with Validation

**What:** Single `yf.download()` call for all tickers per cycle. Validate DataFrame before persisting.
**When to use:** Every fetch cycle. Never loop per-ticker.

```python
# backend/app/services/data_fetcher.py
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone

TICKERS = ["AAPL", "MSFT", "NVDA", "AMD", "GOOGL"]  # full list from domain config

def fetch_all_stocks() -> dict:
    """Batch download. Returns dict of ticker -> price data, or empty on failure."""
    try:
        raw = yf.download(
            TICKERS,
            period="2d",        # 2 days to get at least 1 full trading day
            interval="1d",
            auto_adjust=True,
            progress=False,     # suppress progress bar in logs
            threads=True,
        )
        return validate_and_extract(raw)
    except Exception as e:
        # Log error, return empty — caller uses last-known-good
        return {}

def validate_and_extract(raw: pd.DataFrame) -> dict:
    """Validate DataFrame, return per-ticker dict of latest prices."""
    if raw.empty:
        return {}
    results = {}
    for ticker in TICKERS:
        try:
            # MultiIndex: raw["Close"][ticker]
            close = raw["Close"][ticker].dropna()
            volume = raw["Volume"][ticker].dropna()
            if close.empty or volume.empty:
                continue
            results[ticker] = {
                "close": float(close.iloc[-1]),
                "volume": int(volume.iloc[-1]),
                "fetched_at": datetime.now(timezone.utc),
            }
        except (KeyError, IndexError):
            continue
    return results
```

### Pattern 3: Fallback to Last-Known-Good

**What:** On fetch failure, fetch cycle exits without overwriting DB. API always returns latest DB row.
**When to use:** Any exception in `fetch_all_stocks()` — 429, network failure, Yahoo outage.

```python
# backend/app/scheduler.py
from app.services.data_fetcher import fetch_all_stocks
from app.database import get_sync_session
from app.models.score_snapshot import ScoreSnapshot

def fetch_cycle():
    """Called by APScheduler every 5 minutes."""
    data = fetch_all_stocks()
    if not data:
        # No update — DB retains last-known-good rows
        return
    with get_sync_session() as session:
        for ticker, values in data.items():
            snapshot = ScoreSnapshot(
                ticker=ticker,
                close_price=values["close"],
                volume=values["volume"],
                fetched_at=values["fetched_at"],
            )
            session.add(snapshot)
        session.commit()
```

### Pattern 4: SQLAlchemy 2.0 Models with DeclarativeBase

**What:** Modern SQLAlchemy 2.0 style using `DeclarativeBase` and `Mapped` type annotations.
**When to use:** All new SQLAlchemy models — replaces deprecated `declarative_base()` + `Column`.

```python
# backend/app/models/score_snapshot.py
# Source: SQLAlchemy 2.0 docs — https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Stock(Base):
    __tablename__ = "stocks"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(100))
    domain: Mapped[Optional[str]] = mapped_column(String(50))

class ScoreSnapshot(Base):
    __tablename__ = "score_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(10), index=True)
    close_price: Mapped[float] = mapped_column(Float)
    volume: Mapped[int] = mapped_column(Integer)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
```

### Pattern 5: SQLite WAL Mode via Engine Event

**What:** Enable WAL mode on every new SQLite connection for improved concurrent read performance.
**When to use:** Always with SQLite in a FastAPI app (multiple readers + one scheduler writer).

```python
# backend/app/database.py
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./app.db"
engine = create_async_engine(DATABASE_URL, echo=False)

@event.listens_for(engine.sync_engine, "connect")
def set_wal_mode(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
```

### Anti-Patterns to Avoid

- **Per-ticker yfinance calls in a loop:** Triggers N separate HTTP requests instead of 1 batch. Causes rate limiting immediately. Always pass a list to `yf.download()`.
- **Using `@app.on_event("startup")`:** Deprecated since FastAPI 0.93. Use `lifespan=` parameter with `asynccontextmanager`.
- **Overwriting DB on failed fetch:** If validation returns empty, skip the DB write. The last successful rows are the fallback — don't delete them.
- **Fetching on API request:** Never call yfinance from a route handler. All routes read from the DB cache.
- **Sync SQLAlchemy in async FastAPI routes without threadpool:** Blocks the event loop. Use `async_sessionmaker` + `aiosqlite`, or wrap sync calls with `run_in_threadpool`.
- **Using APScheduler 4.x:** Still pre-release beta as of February 2026. `add_job()` behavior and scheduler classes changed significantly. Stick with 3.10/3.11.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Yahoo Finance HTTP parsing | Custom scraper | `yfinance.download()` | Yahoo changes endpoints frequently; yfinance maintainers track these changes |
| Scheduled background jobs | `threading.Timer` loop | APScheduler | Handles missed jobs, graceful shutdown, timezone awareness, job stores |
| DB schema migrations | Manual `ALTER TABLE` | Alembic | SQLite can't `ALTER` columns; Alembic uses batch migration workaround automatically |
| DataFrame timezone normalization | Custom tz conversion | `df.tz_convert("UTC")` / `df.tz_localize(None)` | pandas 2.2 is strict about tz-aware vs tz-naive mixing; use built-in methods |
| Retry logic for HTTP failures | Custom retry loop | `try/except` + fallback pattern | yfinance doesn't expose retry hooks cleanly; simpler to catch exceptions and use cached data |

**Key insight:** yfinance is a wrapper over an unofficial API that changes without notice. Custom HTTP scrapers are maintenance nightmares. Use yfinance as a black box; design your fallback strategy assuming it will occasionally fail.

---

## Common Pitfalls

### Pitfall 1: Yahoo Finance Rate Limiting (429 errors)

**What goes wrong:** After ~200-400 requests per hour from a single IP, Yahoo returns 429 errors. yfinance raises `YFRateLimitError`. If unhandled, the scheduler crashes and stops polling.
**Why it happens:** Polling too frequently, or making individual ticker requests instead of batching. Each `yf.Ticker(t).history()` call is one HTTP request per ticker.
**How to avoid:** Use `yf.download([...all tickers...])` — one HTTP request for all tickers. At 5-minute intervals with 1 batch call, well under rate limits.
**Warning signs:** `YFRateLimitError` in logs, empty DataFrames returned, `HTTPError: 429` exceptions.

### Pitfall 2: yfinance MultiIndex Column Access

**What goes wrong:** `raw["Close"]` with multiple tickers returns a DataFrame (columns = tickers), not a Series. `raw["Close"]["AAPL"]` is the correct access pattern. Doing `raw["AAPL"]["Close"]` requires `group_by="ticker"` at download time.
**Why it happens:** Default `group_by="column"` puts metric first, ticker second. Developers mix up the levels.
**How to avoid:** Use default `group_by="column"` and access as `raw["Close"][ticker]`. Or use `.stack()` to convert to long format immediately.
**Warning signs:** `KeyError` on DataFrame access, `AttributeError: 'DataFrame' object has no attribute 'Close'`.

### Pitfall 3: Timezone-Naive vs Timezone-Aware Index (pandas 2.2)

**What goes wrong:** pandas 2.2 raises `TypeError` when comparing or joining tz-aware and tz-naive DatetimeIndexes. yfinance may return tz-aware indexes. Storing to SQLite and reading back gives tz-naive.
**Why it happens:** pandas 2.2 tightened tz handling vs 1.x. Mixed tz data causes silent wrong results or crashes.
**How to avoid:** Normalize immediately after download: `df.index = df.index.tz_localize(None)` (if tz-aware, convert to UTC first). Store all timestamps as UTC, display with conversion.
**Warning signs:** `TypeError: Cannot compare tz-naive and tz-aware`, unexpected NaT values.

### Pitfall 4: APScheduler 4.x API Confusion

**What goes wrong:** Developer installs `apscheduler` and gets 4.x (still in pre-release but may appear on PyPI). `BackgroundScheduler` does not exist in 4.x; `add_job()` behaves differently. Code fails at runtime.
**Why it happens:** `pip install apscheduler` may resolve to 4.x pre-release without `--pre` flag depending on PyPI state; version pinning omitted.
**How to avoid:** Pin explicitly: `apscheduler>=3.10,<4.0` in requirements.txt.
**Warning signs:** `ImportError: cannot import name 'BackgroundScheduler'`, `TypeError: add_job()` signature errors.

### Pitfall 5: Scheduler Running Multiple Instances (Gunicorn Multi-Worker)

**What goes wrong:** With multiple uvicorn workers, each worker starts its own APScheduler, causing N simultaneous yfinance fetches every 5 minutes.
**Why it happens:** APScheduler is in-process; multi-worker setups duplicate it.
**How to avoid:** For Phase 1, run single worker (`uvicorn app.main:app --workers 1`). Note this in config. If scaling later, move scheduler to a separate process or use a job lock.
**Warning signs:** Duplicate DB rows with same `fetched_at` timestamp, double the expected fetch frequency.

### Pitfall 6: market-closed data showing as current

**What goes wrong:** After market close, yfinance returns yesterday's close data. If the app shows this as "live" data, users see stale prices without indication.
**Why it happens:** `period="1d"` still returns the last available data point even when market is closed.
**How to avoid:** Store `fetched_at` UTC timestamp on every row. In DATA-05, expose this timestamp in responses. Phase 3 will add the "Market Closed" UI banner — Phase 1 just needs to ensure the timestamp is always present and accurate.
**Warning signs:** Prices unchanging but no staleness indicator, `fetched_at` from yesterday showing as current.

---

## Code Examples

Verified patterns from research and official sources:

### APScheduler 3.x Interval Job — Complete Setup

```python
# backend/app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        fetch_cycle,
        trigger=IntervalTrigger(minutes=5),
        id="data_fetch",
        replace_existing=True,
        max_instances=1,      # prevent overlap if fetch takes >5 min
    )
    return scheduler
```

### yfinance Batch Download — Minimal Verified Pattern

```python
# Based on: https://deepwiki.com/ranaroussi/yfinance/4.2-working-with-multiple-tickers
import yfinance as yf

tickers = ["AAPL", "MSFT", "NVDA"]
raw = yf.download(
    tickers,
    period="2d",
    interval="1d",
    auto_adjust=True,
    progress=False,
    threads=True,
)

# Access pattern for multi-ticker download (group_by="column" is default):
close_prices = raw["Close"]          # DataFrame: columns = tickers
aapl_close = raw["Close"]["AAPL"]   # Series: index = dates

# Convert to long format (pandas 2.2 compatible):
close_long = raw["Close"].stack().rename("close").reset_index()
# Columns: Date, Ticker, close
```

### DataFrame Validation

```python
def validate_ticker_data(raw: pd.DataFrame, ticker: str) -> bool:
    """Return True if ticker data is usable."""
    if raw.empty:
        return False
    try:
        close = raw["Close"][ticker].dropna()
        volume = raw["Volume"][ticker].dropna()
        return not close.empty and not volume.empty and len(close) >= 1
    except KeyError:
        return False
```

### Health Check Endpoint

```python
# backend/app/routers/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.score_snapshot import ScoreSnapshot

router = APIRouter()

@router.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(func.max(ScoreSnapshot.fetched_at))
    )
    last_fetched = result.scalar()
    return {
        "status": "ok",
        "last_fetched": last_fetched.isoformat() if last_fetched else None,
    }
```

### SQLite WAL Mode + Async Engine

```python
# backend/app/database.py
# Source: https://blog.poespas.me/posts/2024/08/04/fastapi-async-db-session-management/
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from collections.abc import AsyncGenerator

DATABASE_URL = "sqlite+aiosqlite:///./app.db"

engine = create_async_engine(DATABASE_URL, echo=False)

@event.listens_for(engine.sync_engine, "connect")
def set_wal_mode(dbapi_connection, _):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `declarative_base()` | `class Base(DeclarativeBase): pass` | SQLAlchemy 2.0 (2023) | Better type inference, IDE support |
| `Column(String)` | `Mapped[str] = mapped_column(String)` | SQLAlchemy 2.0 (2023) | Full type annotation support |
| `@app.on_event("startup")` | `lifespan=asynccontextmanager` function | FastAPI 0.93 (2023) | Old approach still works but shows deprecation warning |
| `yfinance 0.2.x` | `yfinance 1.x` (no API changes) | December 2025 | Pin to `>=1.0`; new config class, better exception types |
| `APScheduler 3.x` | APScheduler 3.x (still current for production) | 4.x pre-release only as of 2026 | Do NOT use 4.x yet |
| `pytz` timezones | `zoneinfo` / UTC-naive for storage | Python 3.9+ / APScheduler 4.x | For Phase 1, use `timezone.utc` from stdlib, store UTC naive in SQLite |

**Deprecated/outdated:**
- `pandas-datareader`: Deprecated Yahoo Finance support, do not use — yfinance replaced it
- `yf.Ticker(t).history()` in a loop: Not deprecated but is the slow path — use `yf.download()` batch
- `BackgroundTasks` (FastAPI built-in): Not a scheduler — no repeat/interval support; use APScheduler for recurring jobs

---

## Open Questions

1. **Should the scheduler use `AsyncIOScheduler` or `BackgroundScheduler`?**
   - What we know: `BackgroundScheduler` runs job in a background thread (sync); `AsyncIOScheduler` runs job as async coroutine in the event loop.
   - What's unclear: If `data_fetcher.py` uses synchronous SQLAlchemy sessions (simpler), `BackgroundScheduler` is natural. If using `async_sessionmaker`, `AsyncIOScheduler` with `async def fetch_cycle()` fits better.
   - Recommendation: Use `BackgroundScheduler` with synchronous SQLAlchemy session for the fetch cycle. yfinance itself is sync. Keep async only for FastAPI routes. This avoids event loop blocking issues.

2. **Use Alembic from Phase 1, or defer?**
   - What we know: `Base.metadata.create_all()` is sufficient if schema won't change. Alembic is required once schema changes are needed.
   - What's unclear: Phase 1 schema is likely stable, but Phase 2/3 will add columns (scores, composite_score).
   - Recommendation: Set up Alembic in Phase 1 even if only `create_all()` is used initially. Retrofitting Alembic into an existing project is painful.

3. **What tickers to seed in Phase 1?**
   - What we know: Domain stock mapping is done in Phase 3. Phase 1 needs some tickers to validate the pipeline works.
   - Recommendation: Hardcode a small representative list (~10 tickers across 2-3 domains) as a seed fixture for testing the pipeline. Phase 3 will replace with full domain mapping.

---

## Sources

### Primary (HIGH confidence)
- PyPI — yfinance page: version 1.2.0 confirmed, no breaking changes from 0.2.x
- GitHub release notes: [yfinance 1.0 release](https://github.com/ranaroussi/yfinance/releases/tag/1.0) — "No breaking changes"
- FastAPI official docs: [Lifespan Events](https://fastapi.tiangolo.com/advanced/events/) — lifespan pattern confirmed
- APScheduler 3.x docs: [User guide](https://apscheduler.readthedocs.io/en/3.x/userguide.html) — BackgroundScheduler, IntervalTrigger
- APScheduler migration docs: [v4 migration](https://apscheduler.readthedocs.io/en/master/migration.html) — 4.x is pre-release, breaking changes confirmed

### Secondary (MEDIUM confidence)
- [DeepWiki yfinance — Working with Multiple Tickers](https://deepwiki.com/ranaroussi/yfinance/4.2-working-with-multiple-tickers) — MultiIndex column access patterns, verified against yfinance source behavior
- [FastAPI async SQLAlchemy example](https://seapagan.github.io/fastapi_async_sqlalchemy2_example/) — WAL mode PRAGMA pattern, `async_sessionmaker` setup
- [Sentry — Schedule tasks with FastAPI](https://sentry.io/answers/schedule-tasks-with-fastapi/) — APScheduler lifespan integration pattern
- [Async DB session management](https://blog.poespas.me/posts/2024/08/04/fastapi-async-db-session-management/) — `get_db` dependency, `expire_on_commit=False`

### Tertiary (LOW confidence — flagged for validation)
- Yahoo Finance rate limits (~200-400 req/hour): Community-reported, no official documentation. Treat as guideline only. Actual limit may vary by IP, time of day, and Yahoo policy changes.
- yfinance `threads=True` performance claims: Community-reported speed improvements; not officially benchmarked.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — versions confirmed via PyPI, official docs
- Architecture: HIGH — patterns from official FastAPI and SQLAlchemy 2.0 docs
- Pitfalls: MEDIUM-HIGH — yfinance pitfalls from GitHub issues + community; APScheduler pitfalls from official migration docs
- Rate limits: LOW — no official Yahoo Finance documentation exists; community-sourced estimates only

**Research date:** 2026-02-17
**Valid until:** 2026-03-17 (30 days; yfinance is fast-moving due to Yahoo scraping changes — check for new releases if blocked)
