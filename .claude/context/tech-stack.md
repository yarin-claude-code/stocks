# Tech Stack

## Backend
- **Python** — primary language
- **FastAPI** — async web framework
- **SQLAlchemy 2.0** — async ORM (`Mapped[T]` / `mapped_column` syntax only)
- **asyncpg** — async Postgres driver (FastAPI routes)
- **psycopg2** — sync Postgres driver (APScheduler thread)
- **Alembic** — migrations
- **APScheduler** — `BackgroundScheduler` for sync yfinance jobs
- **yfinance** — market data (sync, batch via `yf.download()`)
- **pydantic-settings** — config/env management
- **numpy** — ranking math only (`ddof=0` everywhere)
- **pytest + pytest-asyncio** — testing

## Database
- **Supabase Postgres** — port 5432 (direct, NOT pgbouncer 6543)

## Frontend (Phase 3+)
- React (not yet created)

## Infra
- Docker (optional, see `docker/`)
