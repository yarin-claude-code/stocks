# Phase 04 — Context

## Auth UX Flow

| Decision | Detail |
|----------|--------|
| Login/Register UI | Single page (`/login`) with tab/toggle to switch modes |
| Register fields | Email + password + display name |
| Post-login redirect | Always go to `/` (dashboard) |
| Error display | Inline below the relevant form field |

## Preference Sync Behavior

| Decision | Detail |
|----------|--------|
| Save trigger | Auto-save on domain selection change (no Save button) |
| Stale preference | Silent fallback to first available domain |
| Merge on login | Current (unauthenticated) selection saved as preference on first login |
| New user default | First domain in the list |

## Protected Route Handling

| Decision | Detail |
|----------|--------|
| Unauthenticated `/` | Hard redirect to `/login` |
| Post-redirect login | Always go to `/` (not original URL) |
| Logged-in user visits `/login` | Redirect to `/` |
| Protected scope | Dashboard (`/`) only — `/login` is the only public route |

## Session Persistence

| Decision | Detail |
|----------|--------|
| Session storage | Persist in localStorage (Supabase default — survives tab close) |
| Logout button | In a user profile dropdown (header area) |
| Post-logout redirect | Redirect to `/login` |
| Display name | Show in header (e.g. user avatar/name chip in navbar) |
