# API Contracts — Context Reference

## Routes
| Method | Path | Handler | Notes |
|--------|------|---------|-------|
| GET | /api/health | health.py | returns last_fetched timestamp |

## Error Handling
- fetch_all_stocks: returns `{}` on ANY exception (silent fallback)
- Never raises from data fetcher — caller uses last-known-good DB data

## Scheduler
- BackgroundScheduler (NOT AsyncIOScheduler) — yfinance is sync
- Runs fetch_all_stocks on FETCH_INTERVAL_MINUTES cadence
- Registered in lifespan, shutdown(wait=False) on teardown

## FastAPI Lifespan Pattern
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: create_all, seed_db, scheduler.start
    yield
    # shutdown: scheduler.shutdown(wait=False), engine.dispose
```

## yfinance Batch Pattern
- Single yf.download() call for all tickers (avoids rate limits)
- Returns multi-ticker DataFrame — slice per ticker
- validate_ticker_data() uses math.isnan() — pure stdlib, no pandas
