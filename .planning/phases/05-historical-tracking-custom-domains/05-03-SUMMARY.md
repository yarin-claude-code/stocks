---
phase: 05
plan: 03
subsystem: history-ui
tags: [history, recharts, frontend, backend]
dependency_graph:
  requires: [05-01]
  provides: [history-api, history-chart]
  affects: [StockCard]
tech_stack:
  added: [recharts]
  patterns: [TanStack file-based routing, TanStack Query]
key_files:
  created:
    - backend/app/routers/history.py
    - frontend/src/components/TrendBadge.tsx
    - frontend/src/components/ScoreHistoryChart.tsx
    - frontend/src/routes/_authenticated/history.$ticker.tsx
  modified:
    - backend/app/main.py
    - frontend/src/components/StockCard.tsx
decisions:
  - "HistoryPage placed under /_authenticated layout — history is user-facing, login required"
  - "history link in StockCard uses e.stopPropagation() to avoid triggering parent onClick"
metrics:
  duration: 10min
  completed: 2026-02-20
---

# Phase 05 Plan 03: History API + Chart Summary

Recharts score-history chart with trend badge, backed by GET /api/history/{ticker}.

## What Was Built

| Item | Detail |
|------|--------|
| GET /api/history/{ticker} | Returns last N days of DailySnapshot rows ordered by date |
| TrendBadge | Up (slope > 0.5) / Down (slope < -0.5) / Flat badge |
| ScoreHistoryChart | Recharts LineChart, TanStack Query, empty/loading states |
| HistoryPage | /_authenticated/history/$ticker file-based route |
| StockCard link | "View history →" link alongside existing breakdown onClick |

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check

- [x] backend/app/routers/history.py exists
- [x] frontend/src/components/TrendBadge.tsx exists
- [x] frontend/src/components/ScoreHistoryChart.tsx exists
- [x] frontend/src/routes/_authenticated/history.$ticker.tsx exists
- [x] npm run build passes
- [x] Task 1 commit: 134609f
- [x] Task 2 commit: 9ceb097
