# Phase 06: DevOps CI/CD — Research

**Researched:** 2026-02-24
**Domain:** GitHub Actions, Docker, CI pipelines
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- CI runs on every PR
- No CD in this phase — merge to main triggers CI (build + push image) only; deploy is manual
- PR merge blocked if any CI stage fails (branch protection)
- Pipeline stages in order: Lint → pytest → Playwright E2E → Docker build & push
- Docker registry: GitHub Container Registry (ghcr.io)

### Claude's Discretion
- Dockerfile structure (multi-stage builds, base images)
- Nginx reverse proxy setup if needed
- Docker Compose for local dev
- Exact lint tooling (ruff, eslint, etc.)
- Playwright CI setup (headless, browser install)

### Deferred Ideas (OUT OF SCOPE)
- CD (auto-deploy to Hostinger VPS)
- Staging environment
</user_constraints>

---

## Summary

Standard approach: single `.github/workflows/ci.yml` with four sequential jobs (lint, test-backend, test-e2e, docker). Backend uses ruff for linting; frontend uses existing eslint config. Playwright runs headless chromium in CI with `--with-deps`. Docker images use multi-stage builds — backend on `python:3.12-slim`, frontend on `node:22-alpine` builder + `nginx:alpine` runtime. GHCR login uses `GITHUB_TOKEN` (no extra secrets needed). Docker Compose provides local dev stack.

**Primary recommendation:** One workflow file, four jobs with `needs:` chaining. Use ruff (not flake8) for backend lint. Keep Dockerfiles simple — no gunicorn needed for this project scale.

---

## Standard Stack

| Tool | Version | Purpose |
|------|---------|---------|
| `ruff` | latest | Python lint + format check (replaces flake8/black) |
| `eslint` | already in package.json | Frontend TS/TSX lint |
| `docker/login-action` | v3 | GHCR auth via GITHUB_TOKEN |
| `docker/setup-buildx-action` | v3 | Enable BuildKit for multi-stage |
| `docker/build-push-action` | v6 | Build + push to ghcr.io |
| `docker/metadata-action` | v5 | Generate image tags (sha, branch) |

**Add to backend requirements.txt:**
```
ruff>=0.4
```
Or install in CI without adding to requirements: `pip install ruff`

---

## Architecture Patterns

### Workflow Structure
```yaml
# .github/workflows/ci.yml
on:
  pull_request:
  push:
    branches: [main]

jobs:
  lint:        # ruff check backend/ + eslint frontend/
  test-backend:  # pytest backend/tests/
  test-e2e:    # needs: [test-backend], Playwright
  docker:      # needs: [test-e2e], build & push ghcr.io
```

### Job: lint
```yaml
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
  with: { python-version: '3.12' }
- run: pip install ruff && ruff check backend/
- uses: actions/setup-node@v4
  with: { node-version: '22' }
- run: cd frontend && npm ci && npm run lint
```

### Job: test-backend
```yaml
- uses: actions/setup-python@v5
- run: cd backend && pip install -r requirements.txt
- run: cd backend && python -m pytest tests/ -v
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}   # or skip DB tests with mocks
```

### Job: test-e2e
```yaml
- run: cd frontend && npm ci
- run: npx playwright install chromium --with-deps
- run: npx playwright test
  env:
    PLAYWRIGHT_BASE_URL: http://localhost:5173
```
**Key issue:** E2E tests need backend running. Options:
1. Start backend as background process in CI (simplest)
2. Use Docker Compose up in CI step

Recommended: background process — simpler than service containers for this scale.

### Job: docker (build & push)
```yaml
permissions:
  contents: read
  packages: write

- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
- uses: docker/setup-buildx-action@v3
- uses: docker/build-push-action@v6
  with:
    context: ./backend
    push: ${{ github.ref == 'refs/heads/main' }}  # push only on main
    tags: ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
```
Push only on main merge (not on PR builds) — saves registry storage.

### Backend Dockerfile (multi-stage)
```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ ./app/
ENV PYTHONUNBUFFERED=1
EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Frontend Dockerfile (multi-stage)
```dockerfile
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### nginx.conf (frontend SPA routing)
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;  # SPA client-side routing
    }

    location /api/ {
        proxy_pass http://backend:8001;
    }
}
```

### Docker Compose (local dev)
```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    env_file: ./backend/.env
    ports: ["8001:8001"]
  frontend:
    build: ./frontend
    ports: ["80:80"]
    depends_on: [backend]
```

---

## Don't Hand-Roll

| Problem | Use Instead |
|---------|-------------|
| Image tagging strategy | `docker/metadata-action@v5` — handles sha, branch, semver |
| GHCR auth | `GITHUB_TOKEN` — no PAT needed |
| Browser deps in CI | `npx playwright install chromium --with-deps` |
| Python lint | `ruff` — covers flake8 + isort + black in one tool |

---

## Common Pitfalls

### 1. GITHUB_TOKEN missing `packages: write`
Workflow needs explicit `permissions: packages: write` at job level or workflow level, else push to ghcr.io gets 403.

### 2. Docker push on PRs
Push on every PR = registry bloat. Gate with `push: ${{ github.ref == 'refs/heads/main' }}`. PR runs build-only (--load flag), no push.

### 3. Playwright E2E: backend not running
E2E job must start backend before running tests. Simple fix:
```bash
cd backend && uvicorn app.main:app --port 8001 &
sleep 3  # wait for startup
```

### 4. TanStack Router routeTree.gen.ts
The file is auto-generated by the Vite plugin at build time. It exists in the repo (tracked). Vite build in Docker will regenerate it — no special handling needed, but don't gitignore it.

### 5. .dockerignore missing
Without `.dockerignore`, Docker copies `node_modules/` into build context (slow). Always add per-service `.dockerignore`.

### 6. DATABASE_URL in CI pytest
pytest for backend hits actual Supabase DB unless mocked. Either pass `DATABASE_URL` as a GitHub secret or ensure tests mock DB calls. Existing tests should be checked.

---

## Files to Create

```
.github/
  workflows/
    ci.yml
backend/
  Dockerfile
  .dockerignore
frontend/
  Dockerfile
  .dockerignore
  nginx.conf
docker-compose.yml
```

---

## Sources

- [docker/login-action](https://github.com/docker/login-action) — v3, GITHUB_TOKEN auth
- [docker/build-push-action](https://github.com/marketplace/actions/build-and-push-docker-images) — v6
- [Working with Container Registry - GitHub Docs](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [ruff-action GitHub Marketplace](https://github.com/marketplace/actions/ruff-action)
- [Playwright CI docs](https://playwright.dev/docs/ci)
- [Multi-stage FastAPI Docker](https://davidmuraya.com/blog/slimmer-fastapi-docker-images-multistage-builds/)
- [Vite React Docker + nginx](https://www.buildwithmatija.com/blog/production-react-vite-docker-deployment)

## Metadata

**Confidence breakdown:**
- GitHub Actions workflow structure: HIGH — official docs + verified patterns
- GHCR auth via GITHUB_TOKEN: HIGH — official GitHub docs
- Dockerfile patterns: HIGH — multiple verified sources agree
- Playwright CI setup: HIGH — official playwright.dev docs
- E2E backend-in-CI approach: MEDIUM — background process pattern widely used but project's specific test setup not yet written

**Valid until:** 2026-03-24
