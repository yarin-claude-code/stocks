# Phase 4: Authentication & Personalization — Research

**Researched:** 2026-02-20
**Domain:** Supabase Auth + FastAPI JWT + React protected routes
**Confidence:** HIGH

## Summary

Phase 4 adds email/password auth via Supabase Auth. The backend verifies Supabase-issued JWTs on protected routes using PyJWT + FastAPI `Depends`. The frontend uses `@supabase/supabase-js` for sign-up/login/session persistence (auto via localStorage), adds TanStack Router for protected route guards, and stores domain preferences in a new `user_preferences` table in Supabase Postgres with RLS.

The `gotrue` package is deprecated as of Aug 7, 2025. Use `supabase-auth` (package name `supabase_auth`) on the backend. The main `supabase` Python package (v2.28.0, Feb 2026) already uses `supabase_auth` internally — just use `supabase-py` directly; do not add `supabase_auth` as a separate dep unless importing types directly.

**Primary recommendation:** Let Supabase Auth handle all identity (no custom password hashing). FastAPI verifies the JWT locally with PyJWT using the Supabase JWT secret (HS256, audience="authenticated"). Store preferences in a dedicated Postgres table with RLS, not in Supabase `user_metadata`.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| AUTH-01 | Register email/password | `supabase.auth.sign_up()` via `@supabase/supabase-js` on frontend; no backend signup route needed |
| AUTH-02 | Login + JWT | `supabase.auth.sign_in_with_password()` returns access_token; frontend sends as `Authorization: Bearer <token>` |
| AUTH-03 | Session persistence | `@supabase/supabase-js` v2 persists session to localStorage by default; `autoRefreshToken: true` handles renewal |
| AUTH-04 | Save domain preferences | New `user_preferences` table (user_id UUID FK, domains text[]); RLS policy restricts to own rows |
</phase_requirements>

## Standard Stack

### Backend (additions)
| Library | Version | Purpose | Notes |
|---------|---------|---------|-------|
| supabase | 2.28.0 | Python client (wraps supabase_auth) | Already needed; add to requirements.txt |
| PyJWT | 2.8.0+ | Verify Supabase JWT locally | HS256, audience="authenticated" |

### Frontend (additions)
| Library | Version | Purpose | Notes |
|---------|---------|---------|-------|
| @supabase/supabase-js | v2.x | Auth + DB client | Session persistence built-in |
| @tanstack/react-router | v1.x | Protected routes, beforeLoad guard | Phase 3 has no router yet |

**Installation:**
```bash
# Backend
pip install supabase PyJWT

# Frontend
npm install @supabase/supabase-js @tanstack/react-router
```

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| PyJWT | python-jose | python-jose gives better error messages but adds a dep; PyJWT is simpler |
| TanStack Router | React Router v7 | Either works; TanStack Router matches existing TanStack Query ecosystem |
| user_preferences table | Supabase user_metadata | user_metadata is modifiable by the user client-side — security risk for server-trusted data |

## Architecture Patterns

### Auth Flow
```
Frontend                       Backend
  |                               |
  |-- sign_up / sign_in -------> Supabase Auth (hosted)
  |<-- { access_token, refresh_token } --
  |                               |
  |-- GET /api/preferences -----> FastAPI
  |   Authorization: Bearer <JWT>  |
  |                          verify JWT locally (PyJWT)
  |                          query user_preferences WHERE user_id = sub
  |<-- { domains: [...] } --------
```

### FastAPI JWT Dependency
```python
# backend/app/routers/auth.py
import jwt
from fastapi import Depends, HTTPException, Header
from app.config import settings

def get_current_user(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload["sub"]  # Supabase user UUID

# Usage on protected route:
@router.get("/api/preferences")
async def get_preferences(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    ...
```

### Required Settings Addition
```python
# backend/app/config.py — add to Settings:
supabase_url: str
supabase_anon_key: str
supabase_jwt_secret: str  # from Supabase dashboard > Settings > API > JWT Secret
```

### Frontend: Supabase Client Init
```ts
// frontend/src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY,
  { auth: { persistSession: true, autoRefreshToken: true } }
)
```

### Frontend: Protected Routes (TanStack Router)
```tsx
// frontend/src/routes/_authenticated.tsx
import { createFileRoute, redirect } from '@tanstack/react-router'
import { supabase } from '../lib/supabase'

export const Route = createFileRoute('/_authenticated')({
  beforeLoad: async ({ location }) => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) {
      throw redirect({ to: '/login', search: { redirect: location.href } })
    }
    return { session }
  },
})
```

### DB: user_preferences Table
```sql
CREATE TABLE user_preferences (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  domains     text[] NOT NULL DEFAULT '{}',
  updated_at  timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

CREATE POLICY "own_preferences_select" ON user_preferences
  FOR SELECT TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "own_preferences_insert" ON user_preferences
  FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

CREATE POLICY "own_preferences_update" ON user_preferences
  FOR UPDATE TO authenticated
  USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
```

Create as Alembic migration. `auth.users` is Supabase-managed — reference it as FK but do not create it.

### Project Structure (additions)
```
frontend/src/
├── lib/
│   └── supabase.ts          # supabase client singleton
├── routes/
│   ├── __root.tsx
│   ├── index.tsx            # public landing / redirect
│   ├── login.tsx            # sign-in form
│   ├── register.tsx         # sign-up form
│   └── _authenticated/
│       ├── route.tsx        # beforeLoad guard
│       └── dashboard.tsx    # existing dashboard, now protected
backend/app/
├── routers/
│   ├── auth.py              # get_current_user dep, no signup route
│   └── preferences.py       # GET/PUT /api/preferences
└── models/
    └── user_preference.py   # SQLAlchemy model
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Password hashing | bcrypt + custom signup route | Supabase Auth `sign_up()` | Supabase handles email confirm, rate limits, secure storage |
| Token refresh | Custom refresh endpoint | `@supabase/supabase-js` `autoRefreshToken` | Handles token rotation automatically |
| Session storage | Custom cookie/store | Supabase JS client localStorage default | Sync across tabs, auto-expiry handled |
| JWT verification | Custom HMAC check | PyJWT `jwt.decode()` | Handles expiry, audience, algorithm validation |
| Row access control | App-level WHERE clauses | Supabase RLS | Database-enforced, cannot be bypassed by app bugs |

## Common Pitfalls

### Pitfall 1: Wrong JWT audience
**What goes wrong:** PyJWT raises `InvalidAudienceError` — token rejected even though it's valid.
**Cause:** Supabase tokens have `"aud": "authenticated"` — must pass `audience="authenticated"` to `jwt.decode()`.
**Fix:** Always include `audience="authenticated"` in decode call.

### Pitfall 2: RLS blocks service role on test
**What goes wrong:** Unit tests or migrations using the service role key can't read user_preferences.
**Cause:** RLS `authenticated` role policy doesn't apply to `service_role` — service role bypasses RLS entirely. Test client using anon key will be blocked.
**Fix:** Test RLS via the frontend client (anon key + real JWT), not the SQL editor.

### Pitfall 3: `auth.users` FK in Alembic migration
**What goes wrong:** Alembic tries to create FK to `auth.users` but the schema prefix causes errors or autogenerate removes it.
**Cause:** Alembic's autogenerate doesn't track cross-schema FKs by default.
**Fix:** Write the FK migration manually as raw SQL (`op.execute()`), not via autogenerate.

### Pitfall 4: CORS missing Authorization header
**What goes wrong:** Browser blocks preflight for authenticated requests.
**Cause:** Phase 3 CORS config only allows `GET` with `allow_headers=["*"]`. Authenticated routes need `allow_methods=["GET", "PUT"]` and `allow_headers=["Authorization", "Content-Type"]`.
**Fix:** Update CORS middleware in `main.py` when adding auth routes.

### Pitfall 5: gotrue import in existing code
**What goes wrong:** If any existing code imports from `gotrue`, it will diverge from `supabase_auth` post-Aug 2025.
**Cause:** `gotrue` package ceased updates Aug 7, 2025.
**Fix:** Import from `supabase_auth` or use the `supabase` client directly (preferred).

### Pitfall 6: user_metadata for preferences
**What goes wrong:** Storing domain preferences in `user_metadata` — users can overwrite it from the client.
**Cause:** `user_metadata` is modifiable by authenticated users without any server-side guard.
**Fix:** Use the `user_preferences` Postgres table with RLS instead.

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| `gotrue` Python package | `supabase_auth` (via `supabase` package) | Drop-in rename; deprecated Aug 2025 |
| Manual JWT refresh | `autoRefreshToken: true` in supabase-js v2 | No custom token refresh code needed |
| React Router protected routes | TanStack Router `beforeLoad` | Type-safe, integrates with existing TanStack ecosystem |

## Open Questions

1. **TanStack Router migration from Phase 3**
   - Phase 3 built a single App.tsx with no router — TanStack Router needs to wrap the existing dashboard
   - Resolution: wrap Phase 3 dashboard in `_authenticated/dashboard.tsx` route; add `__root.tsx`, `login.tsx`, `register.tsx`

2. **Email confirmation flow**
   - Supabase Auth sends a confirmation email by default on sign_up
   - Decision needed: disable email confirm in Supabase dashboard (simpler for v1) or handle the confirmation redirect
   - Recommendation: disable email confirmation in Supabase dashboard for v1

## Sources

### Primary (HIGH)
- https://pypi.org/project/supabase-auth/ — version 2.28.0, Feb 10 2026, confirms package name
- https://github.com/orgs/supabase/discussions/37798 — deprecation of gotrue, migration to supabase_auth
- https://supabase.com/docs/guides/auth/jwts — JWT signing, audience="authenticated"
- https://tanstack.com/router/v1/docs/framework/react/guide/authenticated-routes — beforeLoad guard pattern
- https://supabase.com/docs/guides/database/postgres/row-level-security — RLS policy syntax

### Secondary (MEDIUM)
- https://phillyharper.medium.com/implementing-supabase-auth-in-fastapi-63d9d8272c7b — PyJWT + FastAPI pattern, verified against official JWT docs
- https://github.com/orgs/supabase/discussions/20763 — HS256 vs JWKS tradeoff discussion

## Metadata

**Confidence breakdown:**
- supabase-auth package status: HIGH — confirmed via PyPI + official GitHub discussion
- JWT verification pattern: HIGH — consistent across official Supabase JWT docs + multiple implementations
- RLS policies: HIGH — official Supabase docs
- TanStack Router protected routes: HIGH — official TanStack docs
- Session persistence: HIGH — official supabase-js v2 docs

**Research date:** 2026-02-20
**Valid until:** 2026-03-20
