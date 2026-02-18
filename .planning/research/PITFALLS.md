# Pitfalls Research

**Date:** 2026-02-17

## Critical Pitfalls

| Pitfall | Cause | Fix | Phase |
|---------|-------|-----|-------|
| Yahoo Finance rate limiting | Per-ticker calls, no caching | `yf.download(all_tickers)` once per cycle, fallback to DB | 1 |
| Naive normalization | Raw values weighted directly | Z-score per factor, ±3σ cap, peer-group only | 2 |
| Volatility direction | High vol → high Z-score (wrong) | Invert raw value before ranking (`-1.0 * rolling_std`) | 2 |
| Stale data | Scheduler fails silently | Always show `fetched_at`, health endpoint, warn if >15 min old | 1 |
| Unjustified weights | Arbitrary choices | Document rationale per weight, show factor breakdown in UI | 2 |
| Survivorship bias | Lists = current winners only | Note limitation; don't claim backtesting accuracy | 1+5 |
| `ticker.info` KeyError | Dict bracket access on missing key | Always `.info.get("trailingPE")` — None is normal | 2 |
| APScheduler multi-worker | Each uvicorn worker starts scheduler | Run `--workers 1`; note in config | 1 |
| SQLite in async routes | Blocks event loop | Use `async_sessionmaker` + aiosqlite (or asyncpg for Postgres) | 1 |

## Acceptable Technical Debt (v1)

- Hardcoded domain→ticker mappings (move to DB in Phase 3)
- JWT in localStorage (read-only app, no financial transactions)
- Single uvicorn worker (scheduler constraint)
