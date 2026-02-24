---
phase: 06-devops
plan: "02"
subsystem: infra
tags: [github-actions, ci, ruff, eslint, playwright, docker, ghcr]

requires:
  - phase: 06-01
    provides: Dockerfiles for backend and frontend images

provides:
  - Four-job CI pipeline (lint -> test-backend -> test-e2e -> docker)
  - ruff linting config for backend Python code
  - Docker image push to ghcr.io on main branch merge only

affects: [deployment, docker]

tech-stack:
  added: [ruff, github-actions, docker/build-push-action@v6, docker/metadata-action@v5]
  patterns: [needs-chain job gating, push-on-main-only pattern, GHA layer cache]

key-files:
  created:
    - .github/workflows/ci.yml
    - backend/ruff.toml
  modified:
    - backend/alembic/env.py
    - backend/app/models/__init__.py
    - backend/app/services/data_fetcher.py
    - backend/app/services/snapshot_service.py
    - backend/tests/test_data_fetcher.py

key-decisions:
  - "ruff rules E/F/I only — permissive, catches real errors not style"
  - "push: github.ref == refs/heads/main — PR builds but never pushes images"
  - "GITHUB_TOKEN for ghcr.io auth — no PAT secret required"
  - "FETCH_INTERVAL_MINUTES: 999 in E2E job — prevents scheduler from running during tests"
  - "GHA layer cache (type=gha) for Docker builds — speeds up repeated CI runs"

patterns-established:
  - "needs: chain: lint -> test-backend -> test-e2e -> docker (failures block downstream)"
  - "noqa comments for intentional E402 late imports in alembic/env.py"

requirements-completed: []

duration: 12min
completed: 2026-02-24
---

# Phase 06 Plan 02: GitHub Actions CI Workflow Summary

**Four-job CI pipeline (lint/test-backend/test-e2e/docker) with ruff config, ghcr.io image push gated on main branch**

## Performance

- **Duration:** 12 min
- **Started:** 2026-02-24T14:59:59Z
- **Completed:** 2026-02-24T15:12:00Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- `.github/workflows/ci.yml` with four jobs and correct needs: chaining
- `backend/ruff.toml` with permissive lint rules (E/F/I, line-length 100)
- Docker push gated on `github.ref == 'refs/heads/main'` — PRs build only

## Task Commits

1. **Task 1: ruff configuration** - `971be6a` (chore)
2. **Task 2: GitHub Actions CI workflow** - `a5a112d` (feat)

## Files Created/Modified
- `.github/workflows/ci.yml` - Four-job CI pipeline
- `backend/ruff.toml` - Ruff linting configuration
- `backend/alembic/env.py` - Added noqa: E402 for late imports
- `backend/app/models/__init__.py` - Explicit re-exports to satisfy F401
- `backend/app/services/data_fetcher.py` - noqa: F821 on pd string annotations
- `backend/app/services/snapshot_service.py` - Removed unused snap= assignment
- `backend/tests/test_data_fetcher.py` - Removed unused result= assignment

## Decisions Made
- ruff rules limited to E/F/I — catches real bugs without style wars
- GITHUB_TOKEN sufficient for ghcr.io push — no PAT secret needed

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Fixed 44 pre-existing ruff errors blocking CI**
- **Found during:** Task 1 (ruff configuration)
- **Issue:** `ruff check backend/` exited non-zero; CI would fail immediately
- **Fix:** Auto-fixed 36 via `ruff --fix`, manually added noqa comments and explicit re-exports for remaining 9
- **Files modified:** alembic/env.py, app/models/__init__.py, app/services/data_fetcher.py, app/services/snapshot_service.py, tests/test_data_fetcher.py
- **Verification:** `ruff check .` exits 0, "All checks passed!"
- **Committed in:** 971be6a (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 2 - missing critical: CI would never pass without clean lint)
**Impact on plan:** Required for CI correctness. No scope creep.

## Issues Encountered
- None beyond the pre-existing lint errors

## User Setup Required
- Add `DATABASE_URL` secret to GitHub repo Settings > Secrets for the E2E job to start the backend

## Next Phase Readiness
- CI pipeline ready; will trigger on next PR to main
- Phase 06-03 (deployment configuration) can proceed
