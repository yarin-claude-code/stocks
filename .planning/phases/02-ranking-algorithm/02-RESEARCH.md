# Phase 2: Ranking Algorithm — Research Summary

**Date:** 2026-02-18 | **Status:** COMPLETE (implemented)

## Key Findings

| Topic | Finding |
|-------|---------|
| Z-score | `numpy` mean/std/clip — no scipy needed. `ddof=0` everywhere (population std). |
| Outlier cap | Cap at `mean ± 3σ` BEFORE Z-scoring, not after. |
| std==0 guard | When all values identical, return `[0.0, ...]` — never divide by zero. |
| Missing factors | Reweight remaining factors proportionally. Never score missing as 0. |
| 0–100 scale | Min-max within peer group. Single stock or all-equal → 50.0. |
| Volatility | INVERT before passing to engine (`-1.0 * rolling_std`). Lower vol = better. |
| financial_ratio | `trailingPE` via `.info.get()` — NOT bracket access. None is the normal case. |
| pegRatio | BROKEN since June 2025 — do not use. |
| period | Changed `fetch_all_stocks` from `2d` → `30d` for momentum/volatility. |
| Pure module | `ranking_engine.py` must NOT import yfinance, DB, or any I/O. |

## Factor Weights

```python
WEIGHT_MOMENTUM          = 0.30   # strongest near-term signal
WEIGHT_VOLUME_CHANGE     = 0.20   # confirms momentum with liquidity
WEIGHT_VOLATILITY        = 0.20   # penalizes instability (inverted)
WEIGHT_RELATIVE_STRENGTH = 0.15   # peer outperformance
WEIGHT_FINANCIAL_RATIO   = 0.15   # valuation anchor (often None → reweighted)
```

## Pitfalls

- `ticker.info["trailingPE"]` → KeyError. Always use `.get()`.
- `pd.Series.std()` defaults `ddof=1` — use `np.std(ddof=0)` explicitly.
- High volatility Z-score = high score (wrong direction) — must invert raw value.
- Rank ties: sort by `(-score, ticker)` for deterministic ordering.
