# Phase 6: DevOps — Context

**Gathered:** 2026-02-24
**Status:** Ready for planning

<domain>
## Phase Boundary

CI/CD pipeline with GitHub Actions: lint, test, Docker build & push. No CD (no auto-deploy to VPS) in this phase. Covers Dockerizing backend + frontend and publishing images to a registry.

</domain>

<decisions>
## Implementation Decisions

### CI/CD Triggers
- CI runs on every PR
- No CD in this phase — merge to main only triggers CI (build + push image), deploy is manual/future
- PRs are blocked from merging if any CI stage fails (branch protection)

### Pipeline Stages (in order)
1. Lint
2. pytest (backend unit tests)
3. Playwright E2E tests
4. Docker build & push (only if all tests pass)

### Docker Registry
- GitHub Container Registry (ghcr.io) — integrated with GitHub Actions, no extra account needed

### PR Policy
- Block merge on failure — all stages required to pass

### Claude's Discretion
- Dockerfile structure (multi-stage builds, base images)
- Nginx reverse proxy setup if needed
- Docker Compose for local dev
- Exact lint tooling (ruff, eslint, etc.)
- Playwright CI setup (headless, browser install)

</decisions>

<specifics>
## Specific Ideas

- "Simple CI" — keep the pipeline straightforward, not over-engineered
- Stages mirror the existing test workflow: lint → pytest → Playwright → build

</specifics>

<deferred>
## Deferred Ideas

- CD (auto-deploy to Hostinger VPS) — future phase
- Staging environment — future phase

</deferred>

---

*Phase: 06-devops*
*Context gathered: 2026-02-24*
