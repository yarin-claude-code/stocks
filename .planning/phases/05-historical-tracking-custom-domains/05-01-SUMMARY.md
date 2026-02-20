---
phase: 05
plan: 01
subsystem: backend
tags: [historical-tracking, scheduler, sqlalchemy, alembic, numpy]
dependency_graph:
  requires: [Phase 03 RankingResult model]
  provides: [DailySnapshot model, daily_snapshots table, compute_trend, snapshot_job]
  affects: [scheduler, Supabase schema]
tech_stack:
  added: [numpy.polyfit for trend slope]
  patterns: [session.merge upsert, CronTrigger at 21:00 UTC]
key_files:
  created:
    - backend/app/models/daily_snapshot.py
    - backend/app/services/snapshot_service.py
    - backend/alembic/versions/05_01_daily_snapshots.py
  modified:
    - backend/app/scheduler.py
decisions:
  - down_revision set to a1c3e7f2b904 (not 8325633ad9d9) to avoid multiple heads
  - domain_map lookup by name resolves domain_id since RankingResult stores domain as string
metrics:
  duration: 15min
  completed: 2026-02-21
---

# Phase 05 Plan 01: Daily Snapshot Infrastructure Summary

DailySnapshot model + Alembic migration + EOD snapshot job wired into scheduler.

## What Was Built

| Artifact | Detail |
|----------|--------|
| DailySnapshot model | Composite PK (ticker, snap_date), trend_slope Float |
| Alembic migration 05_01 | daily_snapshots table with FK to domains.id |
| compute_trend() | np.polyfit slope; 0.0 for <2 points |
| snapshot_job() | Upserts one DailySnapshot per ticker at 21:00 UTC |
| scheduler wiring | CronTrigger(hour=21, minute=0, timezone="UTC") |

## Deviations from Plan

**1. [Rule 1 - Bug] Chained migration from a1c3e7f2b904 instead of 8325633ad9d9**
- Found: multiple heads existed (a1c3e7f2b904 already applied)
- Fix: set down_revision to a1c3e7f2b904 to maintain linear chain
- Files modified: backend/alembic/versions/05_01_daily_snapshots.py

**2. [Rule 2 - Enhancement] Used select() API instead of session.query() for past scores**
- Plan showed legacy query API; used SQLAlchemy 2.0 select() for consistency with codebase
