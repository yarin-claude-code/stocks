# Phase 3: API & Dashboard — Research

**Researched:** 2026-02-19
**Domain:** FastAPI response routes + React/Vite dashboard
**Confidence:** HIGH

## Summary

Phase 3 has two distinct parts: (1) FastAPI routes serving ranking data from the DB, and (2) a new React/Vite frontend consuming those routes. The backend model gap is the critical blocker — `ScoreSnapshot` stores raw price/volume but NOT composite scores or factor breakdowns. Phase 3 must either persist scores in a new DB table during `fetch_cycle()` or compute them on-demand in the route handler. Persisting is simpler and consistent with the existing pattern. The frontend stack is Vite + React-ts + Tailwind v4 + TanStack Query v5, all confirmed current standards for 2026.

**Primary recommendation:** Persist ranking results to a new `RankingResult` table in `fetch_cycle()`. Routes query that table. Frontend polls `/api/rankings` every 5 min via TanStack Query.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DOM-01 | Curated domain list (~10-15) | Expand `seed.py` SEED_DATA — Domain model already exists |
| DOM-02 | Domain → ticker mapping | Stock model already has `domain_id` FK — seed data expansion only |
| UI-01 | Responsive dashboard with top 5 per domain | Tailwind v4 grid + TanStack Query polling `/api/rankings` |
| UI-02 | Click stock → score breakdown | `GET /api/rankings/{domain}` returns per-factor scores; modal or detail panel |
| UI-03 | Loading/skeleton states | Tailwind `animate-pulse` skeleton components while `isLoading` is true |
| UI-04 | "Market Closed" banner | Pure JS `Intl.DateTimeFormat` check against NYSE hours (9:30–16:00 ET, Mon–Fri) |
| UI-05 | Desktop + mobile | Tailwind responsive prefixes (`md:`, `lg:`) — no extra library needed |
</phase_requirements>

## Critical Gap: Score Persistence

`ScoreSnapshot` only stores `close_price`, `volume`, `fetched_at`. Rankings computed in `fetch_cycle()` are logged but never persisted. Phase 3 needs a new model:

```python
# backend/app/models/ranking_result.py
class RankingResult(Base):
    __tablename__ = "ranking_results"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    domain: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    composite_score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    momentum: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume_change: Mapped[float | None] = mapped_column(Float, nullable=True)
    volatility: Mapped[float | None] = mapped_column(Float, nullable=True)
    relative_strength: Mapped[float | None] = mapped_column(Float, nullable=True)
    financial_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
```

Alembic migration required for this table.

## Standard Stack

### Backend (additions to existing)
| Library | Purpose | Notes |
|---------|---------|-------|
| pydantic BaseModel | Response schemas | Already used via FastAPI |
| CORSMiddleware | Allow React dev origin | Add to `main.py` |
| Alembic | New migration for ranking_results | Already set up |

### Frontend (new — does not exist yet)
| Library | Version | Purpose |
|---------|---------|---------|
| Vite | latest | Build tool + dev server |
| React | 19.x | UI framework |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | v4 | Styling — `@tailwindcss/vite` plugin, no `tailwind.config.js` needed |
| @tanstack/react-query | v5 | Data fetching + 5-min polling |

**Installation (frontend):**
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install @tanstack/react-query
npm install tailwindcss @tailwindcss/vite
```

Tailwind v4 CSS import (in `src/index.css`):
```css
@import "tailwindcss";
```

Tailwind v4 Vite plugin (in `vite.config.ts`):
```ts
import tailwindcss from '@tailwindcss/vite'
export default defineConfig({ plugins: [react(), tailwindcss()] })
```

## Architecture Patterns

### Project Structure
```
investment-project/
├── backend/                   # existing
└── frontend/                  # new in Phase 3
    ├── src/
    │   ├── components/
    │   │   ├── DomainSelector.tsx
    │   │   ├── StockCard.tsx
    │   │   ├── ScoreBreakdown.tsx
    │   │   ├── BestOverall.tsx
    │   │   └── Skeleton.tsx
    │   ├── hooks/
    │   │   └── useMarketOpen.ts
    │   ├── api/
    │   │   └── client.ts       # fetch wrappers
    │   ├── App.tsx
    │   └── main.tsx
    ├── vite.config.ts
    └── package.json
```

### Backend Routes
```
GET /api/domains                    → list of domain names
GET /api/rankings                   → top 5 per domain + best overall
GET /api/rankings/{domain}          → all ranked stocks in domain with factor breakdown
GET /api/health                     → last_fetched timestamp (already exists)
```

### Pydantic Response Models
```python
class FactorBreakdown(BaseModel):
    momentum: float | None
    volume_change: float | None
    volatility: float | None
    relative_strength: float | None
    financial_ratio: float | None

class StockRanking(BaseModel):
    ticker: str
    name: str
    composite_score: float
    rank: int
    factors: FactorBreakdown
    computed_at: datetime

class DomainRankings(BaseModel):
    domain: str
    top5: list[StockRanking]

class RankingsResponse(BaseModel):
    domains: list[DomainRankings]
    best_overall: StockRanking
    last_fetched: datetime | None
```

### CORS Setup (add to main.py)
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

### Vite Proxy (dev only — no path rewrite, FastAPI already uses /api prefix)
```ts
// vite.config.ts
server: {
  proxy: {
    '/api': { target: 'http://localhost:8000', changeOrigin: true }
  }
}
```

### TanStack Query Polling (5-min interval)
```tsx
const { data, isLoading } = useQuery({
  queryKey: ['rankings'],
  queryFn: () => fetch('/api/rankings').then(r => r.json()),
  refetchInterval: 300_000,       // 5 minutes — matches backend fetch interval
  refetchIntervalInBackground: false,
})
```

### Market Closed Detection (pure JS, no library)
```ts
// hooks/useMarketOpen.ts
export function isMarketOpen(): boolean {
  const now = new Date()
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/New_York',
    hour: 'numeric', minute: 'numeric', hour12: false, weekday: 'short',
  }).formatToParts(now)
  const p = Object.fromEntries(parts.map(x => [x.type, x.value]))
  const mins = parseInt(p.hour) * 60 + parseInt(p.minute)
  return !['Sat', 'Sun'].includes(p.weekday) && mins >= 570 && mins < 960
}
// Note: does not account for US market holidays (out of scope for v1)
```

### Skeleton Loading (Tailwind animate-pulse — no library)
```tsx
const Skeleton = ({ className }: { className?: string }) => (
  <div className={`animate-pulse rounded bg-gray-200 ${className ?? ''}`} />
)

// Usage in StockCard while isLoading:
<Skeleton className="h-6 w-32" />
<Skeleton className="h-4 w-20 mt-2" />
```

### Responsive Layout (Tailwind only)
```tsx
// Top-5 grid: 1 col mobile → 2 col tablet → 3 col desktop
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
```

## Don't Hand-Roll

| Problem | Use Instead |
|---------|-------------|
| Data fetching + cache + polling | TanStack Query v5 `refetchInterval` |
| CSS utility classes + responsive | Tailwind v4 (no custom CSS grid system) |
| Skeleton animation | Tailwind `animate-pulse` (not a third-party skeleton lib) |
| Timezone conversion | `Intl.DateTimeFormat` (not moment.js or luxon) |
| Vite setup | `npm create vite@latest` template (not manual webpack config) |

## Common Pitfalls

### Pitfall 1: DOMAIN_GROUPS Hardcoded in Scheduler
`fetch_cycle()` currently uses a hardcoded dict. Phase 3 must replace it with a DB query using the sync session pattern (`Session(_sync_engine)`). If not fixed, new domains added to seed data won't be ranked.

### Pitfall 2: No Scores in DB
Route handlers cannot serve composite scores if `fetch_cycle()` doesn't persist them. RankingResult table must be written in `fetch_cycle()` after `rank_domain()` returns.

### Pitfall 3: Tailwind v4 Config Differences
Tailwind v4 has no `tailwind.config.js` and no PostCSS config. Content paths are auto-detected by the Vite plugin. Do not create a config file — it will conflict.

### Pitfall 4: Vite Proxy is Dev-Only
`server.proxy` in `vite.config.ts` only works during `npm run dev`. Production deployment needs CORS headers on FastAPI (already handled) or a reverse proxy (Nginx). Do not rely on Vite proxy in production.

### Pitfall 5: Market Holiday Blindspot
`isMarketOpen()` using only weekday + hour check will show "Market Open" on NYSE holidays (e.g., July 4th). Acceptable for v1 — document as known limitation.

## Seed Data: 10-15 Curated Domains

Expand `seed.py` SEED_DATA to ~12 domains:

| Domain | Example Tickers |
|--------|----------------|
| AI/Tech | AAPL, MSFT, NVDA, AMD, GOOGL |
| EV | TSLA, RIVN, NIO, LCID |
| Finance | JPM, GS, BAC, MS |
| Healthcare | JNJ, PFE, MRNA, UNH |
| Energy | XOM, CVX, NEE, ENPH |
| Consumer | AMZN, WMT, COST, TGT |
| Semiconductors | INTC, QCOM, AVGO, MU |
| Defense | LMT, RTX, NOC, BA |
| Crypto/Fintech | COIN, SQ, PYPL, V |
| Industrials | CAT, DE, HON, GE |
| Media/Streaming | NFLX, DIS, PARA, WBD |
| Real Estate | AMT, PLD, SPG, WELL |

## Sources

### Primary (HIGH)
- Vite official docs — https://vite.dev/config/server-options (proxy config)
- Vite getting started — https://vite.dev/guide/ (react-ts template)
- TanStack Query v5 official — https://tanstack.com/query/v5/docs/framework/react/reference/useQuery
- FastAPI CORS official — https://fastapi.tiangolo.com/tutorial/cors/

### Secondary (MEDIUM)
- Tailwind v4 Vite plugin setup — confirmed via multiple 2025/2026 sources
- NYSE hours 9:30–16:00 ET Mon–Fri — confirmed via official NASDAQ/NYSE sources

## Metadata

**Confidence breakdown:**
- Backend route patterns: HIGH — existing codebase + FastAPI official docs
- React/Vite setup: HIGH — official docs confirmed
- TanStack Query polling: HIGH — official docs confirmed
- Tailwind v4 setup: HIGH — multiple 2026 sources consistent
- Market hours logic: MEDIUM — correct for normal trading days, misses holidays
- Seed domain list: MEDIUM — curated, not from an authoritative source

**Research date:** 2026-02-19
**Valid until:** 2026-03-21 (stable ecosystem)
