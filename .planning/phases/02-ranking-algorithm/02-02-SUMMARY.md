---
phase: 02-ranking-algorithm
plan: 02
subsystem: api
tags: [yfinance, numpy, ranking, scheduler, apscheduler, data-fetcher]

requires:
  - phase: 02-01
    provides: rank_domain(), StockScore, FactorScore — pure ranking engine
provides:
  - compute_factors_for_ticker() in data_fetcher.py
  - 30d yfinance history for factor computation
  - fetch_cycle() calling rank_domain() per domain with INFO logging
affects: [score-api, phase-03-frontend]

tech-stack:
  added: []
  patterns: [per-factor-try-except, pre-inversion-pattern, domain-grouping-in-scheduler]

key-files:
  created: []
  modified:
    - backend/app/services/data_fetcher.py
    - backend/app/scheduler.py

key-decisions:
  - "Pre-invert volatility and financial_ratio in compute_factors_for_ticker() so rank_domain() always receives higher=better values"
  - "DOMAIN_GROUPS defined inside fetch_cycle() for Phase 2 — Phase 3 will replace with DB query"
  - "Second yf.download() in fetch_cycle() for factor computation — simpler than refactoring fetch_all_stocks() to return raw DataFrame"
  - "info.get('trailingPE') — never dict-style access, financial_ratio None is the normal case"

patterns-established:
  - "Per-factor independent try/except: each factor computed independently so one failure doesn't block others"
  - "Pre-inversion at ingestion boundary: factors are inverted before entering ranking engine so engine only deals with higher=better semantics"

requirements-completed: [ALGO-01, ALGO-02, ALGO-03, ALGO-04, ALGO-05, ALGO-06]

duration: 8min
completed: 2026-02-18
---

# Phase 02 Plan 02: Data Fetcher Extension + Scheduler Wiring Summary

**5-factor yfinance computation pipeline wired into APScheduler — momentum, volume_change, inverted-volatility, relative_strength, and inverted-PE fed to rank_domain() per domain on every fetch cycle**

## Performance

- **Duration:** 8 min
- **Started:** 2026-02-18T23:03:35Z
- **Completed:** 2026-02-18T23:11:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Extended `fetch_all_stocks()` from `period="2d"` to `period="30d"` for sufficient momentum/volatility history
- Implemented `compute_factors_for_ticker()` with all 5 factors, each independently try/excepted
- Wired `rank_domain()` per domain inside `fetch_cycle()` with INFO-level logging per ticker
- All 8 ranking engine tests still GREEN after changes

## Task Commits

1. **Task 1: Extend data_fetcher — period=30d + compute_factors_for_ticker()** - `f8310e0` (feat)
2. **Task 2: Wire rank_domain() into fetch_cycle() per domain** - `1cf429c` (feat)

## Files Created/Modified

- `backend/app/services/data_fetcher.py` — Added `import numpy as np`, changed `period="2d"` to `"30d"`, added `compute_factors_for_ticker()` with 5 factors and pre-inversion
- `backend/app/scheduler.py` — Added imports for `yfinance`, `compute_factors_for_ticker`, `rank_domain`; added DOMAIN_GROUPS + ranking block in `fetch_cycle()`

## Decisions Made

- **Pre-invert at ingestion boundary** — volatility (`-1.0 * rolling std`) and financial_ratio (`-1.0 * trailingPE`) are inverted before returning from `compute_factors_for_ticker()`, not inside the ranking engine. The engine always receives higher=better values.
- **Second yf.download() for factors** — fetch_cycle() does a dedicated 30d download for factor computation rather than refactoring fetch_all_stocks() to expose the raw DataFrame. Simpler, no API change.
- **DOMAIN_GROUPS inside fetch_cycle()** — hardcoded for Phase 2; Phase 3 will replace with a DB query when the domain model is exposed via API.
- **info.get('trailingPE') not info['trailingPE']** — yfinance does not guarantee this key; missing PE is the normal case and reweighting fires regularly in production.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Full end-to-end pipeline is complete: yfinance data -> factor computation -> rank_domain() -> logged scores
- Ready for Phase 3 (frontend) to expose ranked scores via REST API
- ScoreSnapshot upsert (Phase 1) continues to work alongside the new ranking pipeline

---
*Phase: 02-ranking-algorithm*
*Completed: 2026-02-18*
