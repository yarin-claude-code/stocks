# Pitfalls Research

**Domain:** Stock ranking / fintech
**Researched:** 2026-02-17
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Yahoo Finance Rate Limiting and Breakage

**What goes wrong:**
yfinance scrapes Yahoo Finance — it's not an official API. Yahoo regularly changes HTML/endpoints, breaking yfinance. Rate limiting kicks in at ~2000 req/hour, returning empty data or errors silently.

**Why it happens:**
Developers call yfinance per-stock, per-request, not batching. Or they don't handle empty/error responses.

**How to avoid:**
- Use `yf.download()` with multiple tickers in one call (batch)
- Cache aggressively — fetch once per 5-min cycle, serve from DB
- Always validate returned data (check for NaN, empty DataFrames)
- Have a fallback: if fetch fails, serve last known good data

**Warning signs:**
Empty DataFrames, NaN values in price data, HTTP 429 errors in logs

**Phase to address:** Phase 1 (data pipeline)

---

### Pitfall 2: Naive Score Normalization

**What goes wrong:**
Scores become meaningless because factors have different scales. Price momentum in % vs volume in millions vs P/E ratios. Raw values can't be compared or weighted.

**Why it happens:**
Developers add raw values together or use simple min-max without considering outliers.

**How to avoid:**
- Z-score normalization per factor (subtract mean, divide by std dev)
- Handle outliers: cap at ±3 standard deviations before normalizing
- Normalize within peer group (same domain), not globally
- Test with edge cases: what happens with only 1 stock? With extreme values?

**Warning signs:**
One factor always dominates the score, rankings don't change when other factors change

**Phase to address:** Phase 2 (algorithm)

---

### Pitfall 3: Survivorship Bias in Domain Stock Lists

**What goes wrong:**
Curated stock lists only include current successful companies. Delisted, bankrupt, or merged stocks are missing, making historical analysis misleading.

**Why it happens:**
Lists are created by looking at "top AI companies today" — not all companies that were ever in the domain.

**How to avoid:**
- For live ranking: this is acceptable (we rank what exists today)
- For historical tracking: note that past scores are for currently-listed stocks only
- Don't claim historical backtesting accuracy
- Re-validate stock lists periodically (tickers change: META was FB)

**Warning signs:**
Historical charts that only go up, ticker symbols returning errors

**Phase to address:** Phase 1 (domain mapping) + Phase with historical features

---

### Pitfall 4: Stale Data Served as Fresh

**What goes wrong:**
App shows rankings from hours/days ago without indicating staleness. Users make decisions on old data.

**Why it happens:**
Scheduler fails silently, no health check, no timestamp on displayed data.

**How to avoid:**
- Always store and display "last updated" timestamp
- Health check endpoint that verifies last successful fetch
- If data is >15 minutes old, show warning banner
- Log fetch failures prominently

**Warning signs:**
"Last updated" timestamp doesn't change, users report stale prices

**Phase to address:** Phase 1 (data pipeline) + Phase with UI

---

### Pitfall 5: Algorithm Weights That Can't Be Justified

**What goes wrong:**
Arbitrary weight choices (why 30% momentum, 20% volume?) that produce questionable rankings. Users (or the developer) can't explain why weights are set as they are.

**Why it happens:**
Weights are picked "by feel" and never validated against any benchmark.

**How to avoid:**
- Document rationale for each weight choice
- Start with equal weights, then adjust based on factor importance reasoning
- Show factor contributions in UI so users can see what's driving scores
- Consider making weights configurable (advanced feature)

**Warning signs:**
Rankings feel random, changing one weight by 5% completely reorders everything

**Phase to address:** Phase 2 (algorithm)

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcoded stock-to-domain mappings | Fast to implement | Hard to update, can't add stocks without code change | v1 MVP only, move to DB in v1.1 |
| SQLite for production | Zero config deployment | Write contention at scale, no concurrent writes | Acceptable for <500 users |
| JWT in localStorage | Simple to implement | XSS vulnerability | Acceptable for non-financial-transaction app (read-only recommendations) |
| No test coverage for algorithm | Ship faster | Regression risk when tuning weights | Never — algorithm IS the product, test from day 1 |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| yfinance | Calling `.info` per stock (slow, rate-limited) | Use `.download()` for batch price data, `.info` only for fundamentals with caching |
| yfinance | Not handling market closed hours | Check market status, serve last close data, don't show "0% change" |
| yfinance | Assuming data is always available | Some tickers return partial data — validate every field before using |
| FastAPI + SQLite | Using synchronous SQLAlchemy in async routes | Use `run_in_executor` or async SQLAlchemy (aiosqlite) |
| React + FastAPI | CORS not configured | Add CORSMiddleware with frontend origin |
| Hostinger VPS | Running uvicorn directly without process manager | Use systemd service + nginx reverse proxy |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Fetching all stock data on every cycle | Slow 5-min cycles, rate limit hits | Batch download, only fetch what changed | >200 stocks being tracked |
| N+1 queries for score display | Slow API responses, DB overload | Eager load scores with stocks in one query | >50 concurrent users |
| No pagination on domain results | Fine with top 5, breaks if expanded | Always LIMIT queries, paginate if expanded | If users want top 20+ |
| Recalculating all scores on every fetch | Wastes CPU, slow cycles | Only recalc for stocks with new data | >500 stocks |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Exposing raw Yahoo Finance data with user IPs | Privacy + TOS violation | Proxy all data through backend, never expose yfinance to frontend |
| No rate limiting on auth endpoints | Brute force attacks | Rate limit /login to 5 attempts/minute |
| Storing passwords in plaintext | Account compromise | bcrypt hashing (passlib) from day 1 |
| No input validation on custom domain stock tickers | Injection, invalid data | Validate tickers against known list or Yahoo Finance lookup |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Showing raw algorithm numbers | Users don't understand z-scores | Normalize to 0-100 scale with labels (Strong Buy/Buy/Hold/Sell) |
| No explanation of what score means | Distrust, confusion | Always show "Why this score?" breakdown |
| Showing data during market closed hours as "live" | Misleading | Clear "Market Closed — showing last close data" banner |
| Too many stocks per domain | Overwhelming, choice paralysis | Top 5 is right — resist expanding to 10+ |
| No loading states | App feels broken during 5-min refresh | Show skeleton/spinner, keep old data visible until new data ready |

## "Looks Done But Isn't" Checklist

- [ ] **Data pipeline:** Often missing error handling for failed fetches — verify graceful degradation
- [ ] **Algorithm:** Often missing edge cases (1 stock in domain, all stocks same price) — verify with edge data
- [ ] **Auth:** Often missing token refresh — verify expired tokens handled gracefully
- [ ] **Rankings:** Often missing "no data available" state — verify empty domain handling
- [ ] **Historical tracking:** Often missing timezone handling — verify all timestamps are UTC
- [ ] **Deployment:** Often missing HTTPS — verify SSL configured on Hostinger

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Yahoo Finance breakage | LOW | Fall back to cached data, alert, wait for yfinance update or switch to httpx direct |
| Bad normalization | MEDIUM | Fix formula, recalculate all historical scores, communicate "scores recalibrated" |
| Data loss (no backups) | HIGH | Set up automated SQLite backups from day 1 |
| Algorithm weights produce bad rankings | LOW | Adjust weights, recalculate — this is tuning, not a bug |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Yahoo Finance rate limiting | Data pipeline phase | Batch fetch works, error handling tested |
| Naive normalization | Algorithm phase | Z-score normalization, outlier handling, unit tests |
| Survivorship bias | Domain mapping phase | Document limitation, validate tickers |
| Stale data | Data pipeline + UI phase | Timestamp displayed, warning on stale data |
| Unjustified weights | Algorithm phase | Weights documented, factor contributions visible |

## Sources

- yfinance GitHub issues (common failure modes)
- Quantitative finance normalization best practices
- Yahoo Finance rate limit community reports
- FastAPI + SQLite deployment patterns
- Fintech UX research

---
*Pitfalls research for: Stock ranking / fintech*
*Researched: 2026-02-17*
