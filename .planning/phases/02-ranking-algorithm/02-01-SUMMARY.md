---
phase: 02-ranking-algorithm
plan: 01
subsystem: ranking-engine
tags: [tdd, algorithm, pure-module, numpy, normalization, ranking]
dependency_graph:
  requires: []
  provides: [ranking-engine]
  affects: [score-api, scheduler-integration]
tech_stack:
  added: []
  patterns: [tdd-red-green, pure-module, dataclasses, numpy-z-score, min-max-scaling, proportional-reweighting]
key_files:
  created:
    - backend/app/services/ranking_engine.py
    - backend/tests/test_ranking_engine.py
  modified: []
decisions:
  - "epsilon tolerance (1e-12) for std==0 guard — np.std of identical floats is ~6.9e-18 not exactly 0.0"
  - "population std ddof=0 everywhere — matches spec requirement"
  - "clip before Z-score — outlier capping uses original mean/std to preserve group statistics"
metrics:
  duration: 3min
  completed: 2026-02-18
---

# Phase 02 Plan 01: Ranking Engine Summary

Pure quantitative ranking engine with Z-score normalization, proportional weight reweighting, min-max scaling, and full FactorScore/StockScore breakdown — proven by 8/8 passing TDD tests.

## What Was Built

`backend/app/services/ranking_engine.py` — isolated pure module (only stdlib + numpy) implementing:

- **FactorScore** dataclass: `raw`, `normalized`, `weighted`, `effective_weight`
- **StockScore** dataclass: `ticker`, `composite_score`, `rank`, `factor_scores`
- **5 named weight constants** summing to 1.0: momentum 0.30, volume_change 0.20, volatility 0.20, relative_strength 0.15, financial_ratio 0.15
- **normalize_factor()**: cap ±3σ → Z-score; std<1e-12 → all zeros; <2 non-None → all None
- **compute_composite()**: exclude None factors, proportionally reweight remaining to sum to 1.0
- **scale_to_0_100()**: min-max within peer group; max==min → all 50.0
- **rank_domain()**: full pipeline; single stock → 50.0/rank-1 shortcut; empty → {}

`backend/tests/test_ranking_engine.py` — 8 test cases:

| Case | Description | Result |
|------|-------------|--------|
| 1 | Single-stock domain | composite_score=50.0, rank=1 |
| 2 | std==0 guard (identical values) | [0.0, 0.0, 0.0], no ZeroDivisionError |
| 3 | Outlier capping at ±3σ | capped Z-score < 5.0 |
| 4 | Missing factor reweighting | effective_weights sum to 1.0 |
| 5 | 0–100 scaling | best=100.0, worst=0.0 |
| 6 | FactorScore structure | all 4 fields present and typed |
| + | Empty domain | returns {} |
| + | Weight constants | sum to 1.0 exactly |

## Decisions Made

**epsilon tolerance for std==0 guard**
numpy `std` of identical float values (e.g. `[0.05, 0.05, 0.05]`) returns `~6.9e-18`, not exactly `0.0`, due to floating-point representation. Using `std < 1e-12` instead of `std == 0.0` correctly catches this case.

**clip using original mean/std before Z-score**
Per spec: cap first, then Z-score. The capped values are divided by the original (uncapped) mean and std, preserving the group's statistical reference frame while bounding extreme outliers.

**financial_ratio None is the normal case**
trailingPE from yfinance is frequently missing. The engine handles this by design — reweighting fires on every real run, not just in edge cases.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed floating-point std==0 comparison**
- **Found during:** GREEN phase — test_normalize_factor_std_zero_returns_all_zeros
- **Issue:** `np.std([0.05, 0.05, 0.05], ddof=0)` returns `6.938893903907228e-18`, not `0.0`. The `std == 0.0` guard did not fire, causing Z-scores of `-1.0` instead of `0.0`.
- **Fix:** Changed guard from `std == 0.0` to `std < 1e-12` (epsilon tolerance).
- **Files modified:** `backend/app/services/ranking_engine.py`
- **Commit:** 2d44d2c

## Task Commits

| Task | Description | Commit |
|------|-------------|--------|
| RED | Failing tests for ranking engine | 8528a03 |
| GREEN | Implement ranking engine (all 8 tests pass) | 2d44d2c |

## Self-Check: PASSED

- backend/app/services/ranking_engine.py: FOUND
- backend/tests/test_ranking_engine.py: FOUND
- Commit 8528a03 (RED): FOUND
- Commit 2d44d2c (GREEN): FOUND
- All 8 tests: PASSED
