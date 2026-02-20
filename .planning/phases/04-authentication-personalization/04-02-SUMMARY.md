---
phase: 04
plan: 02
subsystem: backend
tags: [preferences, auth, fastapi]
requires: [04-01]
provides: [GET /api/preferences, PUT /api/preferences]
affects: [backend/app/main.py]
tech-stack-added: []
tech-stack-patterns: [Depends(get_current_user), async SQLAlchemy upsert]
key-files-created: [backend/app/routers/preferences.py]
key-files-modified: [backend/app/main.py]
decisions:
  - Upsert pattern (select then insert-or-update) for UserPreference rows
  - First-time users return empty list (200), not 404
duration: 5min
completed: 2026-02-20
---

# Phase 04 Plan 02: Preferences Endpoints Summary

**One-liner:** GET + PUT /api/preferences endpoints protected by JWT dependency, with upsert logic for UserPreference rows.

## What Was Built

- `backend/app/routers/preferences.py` — GET returns user's saved domains (empty list for new users); PUT upserts the list
- `backend/app/main.py` — preferences router registered; allow_methods already included GET/PUT

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Select-then-insert upsert | Avoids ON CONFLICT complexity; async sessions don't support merge() |
| Empty list on missing row | Plan spec: first-time users get 200 + `[]`, not 404 |

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- `backend/app/routers/preferences.py` exists
- Routes `/api/preferences` (GET + PUT) registered in app
- Commits: 938ef72, 4a49fe5
