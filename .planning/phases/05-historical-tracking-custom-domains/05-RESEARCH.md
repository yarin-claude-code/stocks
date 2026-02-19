# Phase 5: Historical Tracking & Custom Domains — Research

**Researched:** 2026-02-20
**Domain:** PostgreSQL snapshots, Recharts, APScheduler cron, Supabase RLS, yfinance validation
**Confidence:** HIGH

---

## Summary

Six focused decisions drive this phase. All are resolved below with single prescriptive answers. No user CONTEXT.md — all choices are at planner's discretion.

**Primary recommendation:** Separate `DailySnapshot` table (not reuse RankingResult), CronTrigger EOD job, Recharts for charts, `user_domains` table with RLS, `yf.Ticker.info` for validation.

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DOM-03 | Custom domains (user-defined) | `user_domains` + `user_domain_tickers` tables with RLS |
| DOM-04 | Ticker validation | `yf.Ticker(symbol).info` spot check before saving |
| HIST-01 | Daily score snapshots | `DailySnapshot` table, CronTrigger EOD job writes one row/ticker/day |
| HIST-02 | Score history chart | Recharts `LineChart` + TanStack Query `useQuery` |
| HIST-03 | Trend indicators | 7-day linear slope on `DailySnapshot.composite_score` |
</phase_requirements>

---

## Decision 1: Snapshot Storage — New Table vs Reuse RankingResult

**Recommendation:** New `DailySnapshot` table — one row per (ticker, date).

| Option | Verdict |
|--------|---------|
| Reuse `RankingResult` (5-min rows) | Bloats table; mixing intraday + daily granularity; query complexity high |
| New `DailySnapshot` with `DATE` column | Clean separation; PK `(ticker, snap_date)` gives free dedup + fast range queries |

**Schema:**
```sql
CREATE TABLE daily_snapshots (
    ticker      VARCHAR(10)  NOT NULL,
    snap_date   DATE         NOT NULL,
    composite_score FLOAT    NOT NULL,
    rank        INTEGER      NOT NULL,
    domain_id   INTEGER      REFERENCES domains(id),
    PRIMARY KEY (ticker, snap_date)
);
```

Index `(ticker, snap_date)` via PK is sufficient at this data volume. No TimescaleDB needed for v1.

---

## Decision 2: EOD Snapshot Job — Separate or Derived from fetch_cycle

**Recommendation:** Add a second job to the existing `BackgroundScheduler` using `CronTrigger`.

- `fetch_cycle` runs every 5 min (interval trigger) — unchanged
- New `snapshot_job` runs once daily at market close (e.g., 21:00 UTC = ~4pm ET + buffer)
- `snapshot_job` queries latest `RankingResult` per ticker per domain → inserts one `DailySnapshot` row if not already present (upsert on PK conflict)

```python
from apscheduler.triggers.cron import CronTrigger

scheduler.add_job(snapshot_job, CronTrigger(hour=21, minute=0, timezone="UTC"))
```

**Do not** derive by aggregating RankingResult in the API — that couples query perf to history length. Write-at-EOD, read-precomputed is the right pattern.

---

## Decision 3: Chart Library

**Recommendation:** Recharts (`recharts` v2.x).

- Native React components, SVG-based, no wrapper overhead
- `LineChart` + `ResponsiveContainer` + TanStack Query `useQuery` is the standard pattern
- Already aligns with Tailwind v4 styling (CSS class on SVG elements)
- Chart.js is Canvas-based and better for huge datasets — not relevant here (30–90 day window)

```bash
npm install recharts
```

```tsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

// data: { date: string; score: number }[]
<ResponsiveContainer width="100%" height={300}>
  <LineChart data={data}>
    <XAxis dataKey="date" />
    <YAxis domain={[0, 100]} />
    <Tooltip />
    <Line type="monotone" dataKey="score" stroke="#6366f1" dot={false} />
  </LineChart>
</ResponsiveContainer>
```

---

## Decision 4: Trend Indicators Computation

**Recommendation:** 7-day linear slope — computed in Python, stored in `DailySnapshot` or returned by API.

- "Today vs yesterday" is too noisy (single-day swings)
- 7-day slope is simple, explainable, no ML
- Compute with numpy `np.polyfit(x, y, 1)[0]` where x=day indices, y=composite_score
- Return `trend_slope: float` and derive label in frontend: `> 0.5` → up, `< -0.5` → down, else flat
- Store slope on `DailySnapshot` row (compute at write time, not query time)

```python
import numpy as np

def compute_trend(scores: list[float]) -> float:
    """7-day linear slope. Returns 0.0 if fewer than 2 points."""
    if len(scores) < 2:
        return 0.0
    x = np.arange(len(scores), dtype=float)
    slope, _ = np.polyfit(x, scores, 1)
    return float(slope)
```

---

## Decision 5: Custom Domains Storage

**Recommendation:** Two new tables with RLS — `user_domains` and `user_domain_tickers`.

```sql
CREATE TABLE user_domains (
    id         SERIAL PRIMARY KEY,
    user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name       TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE user_domain_tickers (
    domain_id  INTEGER REFERENCES user_domains(id) ON DELETE CASCADE,
    ticker     VARCHAR(10) NOT NULL,
    PRIMARY KEY (domain_id, ticker)
);

ALTER TABLE user_domains ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_domain_tickers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users own their domains" ON user_domains FOR ALL TO authenticated
  USING ((select auth.uid()) = user_id)
  WITH CHECK ((select auth.uid()) = user_id);

CREATE POLICY "Users access their domain tickers" ON user_domain_tickers FOR ALL TO authenticated
  USING (domain_id IN (SELECT id FROM user_domains WHERE user_id = (select auth.uid())));
```

**Do not** extend `user_preferences` JSONB — relational tables are queryable, indexable, and RLS-safe.

Index `user_domains(user_id)` — required for RLS policy performance.

---

## Decision 6: Ticker Validation

**Recommendation:** `yf.Ticker(symbol).info` with a `shortName` presence check.

- `yf.download()` spot-check is slower and returns a DataFrame — overkill for validation
- `ticker.info` returns a dict; invalid tickers return `{}` or `{'trailingPegRatio': None}` with no `shortName`
- Wrap in try/except — yfinance raises on network errors

```python
import yfinance as yf

def validate_ticker(symbol: str) -> bool:
    """Returns True if ticker exists on Yahoo Finance."""
    try:
        info = yf.Ticker(symbol.upper()).info
        return bool(info.get("shortName") or info.get("longName"))
    except Exception:
        return False
```

**Important:** Run this in the scheduler thread (sync context) or a `run_in_executor` call — yfinance is sync, cannot call from async route handler directly.

---

## Standard Stack

| Library | Version | Purpose |
|---------|---------|---------|
| recharts | ^2.x | Score history line chart |
| apscheduler | existing | Add CronTrigger for EOD job |
| yfinance | existing | Ticker validation via `.info` |
| numpy | existing | 7-day slope via `np.polyfit` |

No new backend dependencies. Frontend adds only `recharts`.

---

## Architecture Patterns

### Backend additions
```
backend/app/
├── services/
│   ├── snapshot_service.py   # snapshot_job(), compute_trend()
│   └── ticker_validator.py   # validate_ticker()
├── models/
│   └── daily_snapshot.py     # DailySnapshot SQLAlchemy model
└── routers/
    └── history.py            # GET /api/history/{ticker}, GET /api/domains/custom
```

### Frontend additions
```
frontend/src/
├── components/
│   ├── ScoreHistoryChart.tsx  # Recharts LineChart wrapper
│   └── TrendBadge.tsx        # up/flat/down indicator
├── routes/
│   └── history.$ticker.tsx   # TanStack Router page
└── api/
    └── history.ts            # TanStack Query hooks
```

---

## Don't Hand-Roll

| Problem | Use Instead |
|---------|-------------|
| Trend computation | `np.polyfit` — not manual slope math |
| Chart rendering | Recharts — not D3 or canvas directly |
| RLS policy enforcement | Supabase DB policies — not app-layer filtering |
| Ticker dedup on upsert | `ON CONFLICT (ticker, snap_date) DO NOTHING` — not SELECT-then-INSERT |

---

## Common Pitfalls

### Pitfall 1: RLS on `user_domain_tickers` misses join path
Policy must check via subquery to `user_domains`. Direct `user_id` column on tickers table adds update complexity.

### Pitfall 2: yfinance `.info` returns partial dict for delisted tickers
Check `shortName` OR `longName` — not just non-empty dict. Some invalid symbols return a dict with only `None` values.

### Pitfall 3: XAxis category vs number in Recharts
For date strings as x-axis: use `type="category"` (default). For Unix timestamps: use `type="number"` with a `tickFormatter`. Date strings are simpler here — ISO format `YYYY-MM-DD` sorts correctly as category.

### Pitfall 4: snapshot_job fires before markets close
Use UTC 21:00 (4pm ET + 1h buffer) to ensure day's final `RankingResult` rows exist.

### Pitfall 5: Trend slope with fewer than 7 days of data
`compute_trend` must guard on `len(scores) < 2` and return `0.0` — polyfit requires at least 2 points.

---

## Open Questions

1. **User domain ranking cycle** — when a user creates a custom domain, does it get ranked in the next `fetch_cycle` automatically, or on-demand?
   - Recommendation: auto-include in `fetch_cycle` by reading all domains (built-in + user) from DB

2. **History retention** — how many days of DailySnapshot to keep?
   - Recommendation: 90 days for v1, no purge job needed at this scale

---

## Sources

### Primary (HIGH)
- [Supabase RLS Docs](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [APScheduler 3.x User Guide](https://apscheduler.readthedocs.io/en/3.x/userguide.html)
- [yfinance Ticker Reference](https://ranaroussi.github.io/yfinance/reference/yfinance.ticker_tickers.html)

### Secondary (MEDIUM)
- [PostgreSQL Time-Series Best Practices — Alibaba Cloud](https://www.alibabacloud.com/blog/postgresql-time-series-best-practices-stock-exchange-system-database_594815)
- [Recharts Ultimate Guide — CodeParrot](https://codeparrot.ai/blogs/recharts-the-ultimate-react-charting-library)
- [Top React Chart Libraries 2026 — Syncfusion](https://www.syncfusion.com/blogs/post/top-5-react-chart-libraries)

---

## Metadata

**Confidence breakdown:**
- Snapshot table design: HIGH — standard PostgreSQL pattern, verified with multiple sources
- APScheduler CronTrigger: HIGH — official docs confirm BackgroundScheduler + CronTrigger is correct
- Recharts: HIGH — consistent recommendation across 2025/2026 sources for React dashboards
- Trend computation: HIGH — numpy polyfit is standard, no ML needed
- Custom domains RLS: HIGH — Supabase official docs + production pattern verified
- Ticker validation: MEDIUM — yfinance `.info` behavior on invalid tickers is empirically documented but yfinance API is unofficial

**Research date:** 2026-02-20
**Valid until:** 2026-03-20
