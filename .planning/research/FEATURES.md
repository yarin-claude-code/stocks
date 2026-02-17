# Feature Research

**Domain:** Stock ranking / screening
**Researched:** 2026-02-17
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Stock scores with clear ranking | Core promise of the app | MEDIUM | Weighted composite score, normalized 0-100 |
| Domain/sector filtering | Users want stocks relevant to their interests | LOW | Curated list + custom |
| Top N display per category | Standard screener pattern | LOW | Top 5 per domain |
| Score breakdown/explanation | Users distrust black-box scores | MEDIUM | Show each factor's contribution |
| Data freshness indicator | Users need to know data age | LOW | "Last updated X min ago" |
| Mobile-responsive layout | Majority of retail investors check on mobile | LOW | Tailwind handles this |
| Basic auth with saved preferences | Return users expect persistence | MEDIUM | JWT + domain selections saved |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| "Best Overall Investment Today" | Single actionable pick — most screeners overwhelm with data | LOW | Highest composite score across all domains |
| Domain-based organization | Most screeners use sectors; domains (AI, Sports) are more intuitive for retail | LOW | Mapping stocks to interest domains is unique |
| Mathematical score explanation | Most tools show scores without explaining the math | MEDIUM | Formula breakdown per stock |
| Historical score tracking | See how scores changed over time — was this stock rising in rank? | MEDIUM | Daily snapshots, trend visualization |
| Custom domain creation | User maps their own stocks to custom categories | MEDIUM | Needs stock ticker validation |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Real-time streaming prices | "More data = better" | Massive complexity, Yahoo Finance can't support it, 5-min is sufficient for ranking | Show clear "as of" timestamp, explain ranking doesn't need real-time |
| ML/AI predictions | Buzzword appeal | Unexplainable, unreliable, overfitting risk, contradicts core value | Transparent mathematical formula |
| Social sentiment integration | "Everyone does it" | Noisy signal, API costs, manipulation-prone | Pure market-data signals only |
| Portfolio tracking | "While I'm here..." | Scope creep, liability concerns, different product | Link to external portfolio tools |
| Price alerts | Standard fintech feature | Requires persistent connections, notification infra | Defer to v2+ if needed |
| Backtesting | "Prove it works" | Survivorship bias, look-ahead bias, complex to do correctly | Show historical scores, not hypothetical returns |

## Feature Dependencies

```
[Domain Selection]
    └──requires──> [Stock-to-Domain Mapping]
                       └──requires──> [Yahoo Finance Data Pipeline]

[Score Calculation]
    └──requires──> [Yahoo Finance Data Pipeline]
    └──requires──> [Normalization Engine]

[Score Explanation]
    └──requires──> [Score Calculation]

[Historical Tracking]
    └──requires──> [Score Calculation]
    └──requires──> [Database Storage]

[Best Overall Pick]
    └──requires──> [Score Calculation across all domains]

[Auth + Preferences]
    └──independent (can be built in parallel)

[Custom Domains]
    └──requires──> [Auth] (need to save per-user)
    └──requires──> [Stock Ticker Validation]
```

### Dependency Notes

- **Score Calculation requires Data Pipeline:** Can't rank without data — pipeline is phase 1
- **Historical Tracking requires Database:** Need storage before we can track over time
- **Custom Domains requires Auth:** Anonymous users can't save custom domains
- **Score Explanation requires Score Calculation:** Must understand scoring to explain it

## MVP Definition

### Launch With (v1)

- [ ] Yahoo Finance data pipeline (fetch, cache, serve)
- [ ] Quantitative ranking algorithm with 5 factors
- [ ] Curated domain list with stock mappings
- [ ] Top 5 per domain display
- [ ] Best Overall Investment Today
- [ ] Score breakdown showing factor contributions
- [ ] Basic responsive UI

### Add After Validation (v1.x)

- [ ] Simple auth (login to save preferences)
- [ ] Custom domain creation
- [ ] Historical score tracking + daily charts
- [ ] Score trend indicators (rising/falling)

### Future Consideration (v2+)

- [ ] Price alerts
- [ ] Backtesting (if done correctly)
- [ ] Additional data sources beyond Yahoo Finance
- [ ] Comparison mode (compare 2 stocks side-by-side)

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Data pipeline + caching | HIGH | MEDIUM | P1 |
| Ranking algorithm | HIGH | HIGH | P1 |
| Domain selection (curated) | HIGH | LOW | P1 |
| Top 5 + Best Overall display | HIGH | LOW | P1 |
| Score breakdown | HIGH | MEDIUM | P1 |
| Responsive UI | MEDIUM | LOW | P1 |
| Auth + preferences | MEDIUM | MEDIUM | P2 |
| Historical tracking | MEDIUM | MEDIUM | P2 |
| Custom domains | MEDIUM | MEDIUM | P2 |
| Score trends | LOW | LOW | P2 |

## Competitor Feature Analysis

| Feature | Finviz | Stock Rover | Our Approach |
|---------|--------|-------------|--------------|
| Screening | Filter-based, 60+ criteria | Deep fundamental screening | Domain-based, algorithm-ranked (simpler, more opinionated) |
| Scoring | Heat maps, no single score | Proprietary scores | Single composite score, fully explained |
| Data freshness | Real-time (paid) | 15-min delay | 5-min polling, clearly labeled |
| Explanation | None — raw data | Some tooltips | Full mathematical breakdown per stock |
| Organization | Sectors (GICS) | Sectors + custom screeners | Interest domains (AI, Sports, etc.) — more intuitive |

## Sources

- Finviz.com feature analysis
- Stock Rover feature comparison
- TradingView screener capabilities
- Seeking Alpha quant ratings approach
- Retail investor UX research patterns

---
*Feature research for: Stock ranking / screening*
*Researched: 2026-02-17*
