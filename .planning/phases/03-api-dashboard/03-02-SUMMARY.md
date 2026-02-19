---
phase: 03-api-dashboard
plan: "02"
subsystem: backend-api
tags: [fastapi, routing, cors, pydantic]
dependency_graph:
  requires: [03-01]
  provides: [03-03]
  affects: [backend/app/main.py]
tech_stack:
  added: []
  patterns: [pydantic-response-models, scalar-subquery-for-latest]
key_files:
  created:
    - backend/app/routers/domains.py
    - backend/app/routers/rankings.py
  modified:
    - backend/app/main.py
decisions:
  - scalar_subquery for latest computed_at — single query, no Python-side max
  - defaultdict grouping by domain in memory — simpler than subquery GROUP BY
  - 404 on empty domain — not empty list, per spec
metrics:
  duration: 15min
  completed: 2026-02-20
---

# Phase 03 Plan 02: API Routes Summary

GET /api/domains, /api/rankings, /api/rankings/{domain} + CORS middleware.

## What Was Built

| Artifact | Detail |
|----------|--------|
| `routers/domains.py` | GET /api/domains — sorted domain names from DB |
| `routers/rankings.py` | GET /api/rankings (top5/domain + best_overall), GET /api/rankings/{domain} (all, 404 if missing) |
| `main.py` | CORSMiddleware (localhost:5173, GET only) + router registration |

## Decisions Made

| Decision | Why |
|----------|-----|
| scalar_subquery for latest computed_at | One query, DB does the max |
| In-memory groupby after query | Simpler than window functions for top-5 |
| 404 for unknown domain | Spec requires it — empty list would hide errors |

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check

- `backend/app/routers/domains.py` — FOUND
- `backend/app/routers/rankings.py` — FOUND
- `backend/app/main.py` — FOUND (CORS + routers verified via python -c)
- Commits: c218aed (routers), 1812d4d (main.py)
