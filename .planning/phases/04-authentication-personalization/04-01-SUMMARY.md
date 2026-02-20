---
phase: 04
plan: 01
subsystem: backend-auth
tags: [jwt, supabase, rls, auth]
requires: []
provides: [get_current_user dependency, user_preferences table]
affects: [backend/app/config.py, backend/app/main.py]
tech-stack-added: [PyJWT==2.8.0]
tech-stack-patterns: [Supabase JWT HS256 decode, Alembic raw SQL for auth.users FK + RLS]
key-files-created:
  - backend/app/routers/auth.py
  - backend/app/models/user_preference.py
  - backend/alembic/versions/8325633ad9d9_add_user_preferences.py
key-files-modified:
  - backend/app/config.py
  - backend/app/main.py
  - backend/requirements.txt
decisions:
  - "Split op.execute() calls — asyncpg rejects multiple SQL commands in one prepared statement"
  - "Raw SQL migration for user_preferences to handle auth.users FK (Supabase schema) and RLS"
metrics:
  duration: 4min
  completed: 2026-02-20
  tasks: 2
  files: 6
---

# Phase 04 Plan 01: JWT Auth Foundation Summary

Supabase JWT verification dependency + user_preferences table with RLS in Supabase Postgres.

## What Was Built

- `get_current_user` FastAPI dependency: validates `Authorization: Bearer <token>` via PyJWT HS256 decode with `audience="authenticated"`, returns user UUID (`sub` claim)
- `UserPreference` SQLAlchemy model: UUID PK, `user_id` (FK to `auth.users`), `domains` text[], `updated_at` timestamptz
- Alembic migration: raw SQL creates `user_preferences` table, enables RLS, creates row-ownership policy
- Settings extended with `supabase_url`, `supabase_anon_key`, `supabase_jwt_secret`
- CORS updated to allow `PUT` method

## Decisions Made

| Decision | Reason |
|----------|--------|
| Split `op.execute()` per statement | asyncpg raises `PostgresSyntaxError` on multi-command prepared statements |
| Raw SQL migration (not autogenerate) | `auth.users` is in Supabase's `auth` schema — SQLAlchemy metadata can't reference it |
| PyJWT 2.8.0 | Stable, no cryptography extras needed for HS256 |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Split multi-statement op.execute() for asyncpg compatibility**
- Found during: Task 2 (alembic upgrade head)
- Issue: asyncpg does not support multiple SQL commands in a single prepared statement
- Fix: Split CREATE TABLE, ALTER TABLE, and CREATE POLICY into separate `op.execute()` calls
- Files modified: `backend/alembic/versions/8325633ad9d9_add_user_preferences.py`
- Commit: c72441d

## Next Step

Plan 04-02: Preferences API endpoints (GET/PUT `/api/preferences`) using `get_current_user`.
