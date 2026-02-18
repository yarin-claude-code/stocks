# Hard Constraints

## Architecture
- `ranking_engine.py` must be pure: no `app.database`, `app.models`, `yfinance` imports — only `dataclasses`, `typing`, `numpy`
- Two-engine pattern: async engine (asyncpg) for FastAPI; sync engine (psycopg2) for scheduler
- Never use `AsyncIOScheduler` for yfinance jobs (yfinance is sync)
- Never mix session types: async sessions in routes only, sync sessions in scheduler only

## Math
- `ddof=0` everywhere (population std, not sample std)
- No scipy — only numpy
- No ML/neural networks — explainable math only

## Database
- Supabase port **5432** only (not 6543)
- SQLAlchemy 2.0 `Mapped[T]` / `mapped_column` — never legacy `Column`

## Data / API
- No websocket streaming — 5-min polling is sufficient
- `fetch_all_stocks` returns `{}` on any exception (silent fallback, never raises)

## Code Quality
- No magic numbers in ranking engine — all weights are named module-level constants
- Idempotent seeds: select-then-insert
- Tests run from `backend/` working directory

## Weights (must sum to 1.0)
```
WEIGHT_MOMENTUM          = 0.30
WEIGHT_VOLUME_CHANGE     = 0.20
WEIGHT_VOLATILITY        = 0.20   # inverted before passing in
WEIGHT_RELATIVE_STRENGTH = 0.15
WEIGHT_FINANCIAL_RATIO   = 0.15   # inverted; None is normal case
```
