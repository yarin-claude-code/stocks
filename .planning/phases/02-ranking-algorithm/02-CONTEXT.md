# Phase 2: Ranking Algorithm - Context

**Gathered:** 2026-02-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Build an isolated, testable ranking engine (`backend/services/ranking_engine.py`) that:
- Normalizes 5 stock factors via Z-score with ±3 std dev outlier capping
- Computes a weighted composite score (0–100 scale)
- Ranks stocks within their peer domain (not globally)
- Exposes a per-factor score breakdown data structure
- Is covered by a comprehensive pytest test suite

Storing scores to DB and exposing via API are in Phase 3.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion
User has explicitly delegated all implementation decisions to Claude. Apply engineering best practices throughout:

- **Factor weights** — Claude chooses weights with documented rationale in code comments. Suggested starting point: price momentum 30%, volume change 20%, volatility 20%, sector relative strength 15%, financial ratios 15%. Weights must sum to 1.0 and be defined as named constants.
- **Score interpretation** — Scores are relative within the peer domain on a given run (not cumulative). A score of 100 = best in domain that day, 0 = worst. Scores reset each calculation cycle.
- **Peer group edge cases** — If a domain has only 1 stock, it scores 50 (midpoint, neutral). If 2 stocks, normal Z-score applies. Document this behavior.
- **Missing data policy** — If a factor value is NaN/missing for a stock, exclude that factor from the composite and reweight remaining factors proportionally. Never silently score 0 for missing data.
- **Score breakdown structure** — Return a dict/dataclass with `composite_score`, `rank`, `factor_scores: {factor_name: {raw, normalized, weighted}}` for each factor.

</decisions>

<specifics>
## Specific Ideas

No specific requirements — user has delegated all decisions to Claude's discretion.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-ranking-algorithm*
*Context gathered: 2026-02-18*
