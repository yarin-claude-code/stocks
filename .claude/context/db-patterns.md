# Database Patterns — Context Reference

## Two-Engine Pattern (NEVER mix these)
| Engine | Type | Used in |
|--------|------|---------|
| `async_session_maker` (asyncpg) | Async | FastAPI route handlers ONLY |
| `Session(_sync_engine)` (psycopg2) | Sync | APScheduler thread ONLY |

## Connection
- Port: **5432** (direct Postgres) — NOT 6543 (pgbouncer)
- sync_database_url auto-derived: replace `asyncpg` → `psycopg2` in Settings

## Migration Workflow
```bash
cd backend
alembic current          # check state
alembic revision --autogenerate -m "description"
alembic upgrade head
python -m pytest tests/ -v
```

## Alembic URL Injection
- configparser cannot read env vars — URL injected programmatically in env.py
- env.py calls load_dotenv() THEN config.set_main_option()

## Session Rules
- Route handlers: `async with async_session_maker() as session:`
- Scheduler: `with Session(_sync_engine) as session:`
- scheduler.shutdown(wait=False) — prevents blocking on active fetch

## Seeding
- seed_db() is idempotent — select-then-insert, safe to rerun
