# Ranking Engine — Context Reference

## Factor Weights (must sum to 1.0)
| Constant | Weight | Input |
|----------|--------|-------|
| WEIGHT_MOMENTUM | 0.30 | 5-day price return |
| WEIGHT_VOLUME_CHANGE | 0.20 | 5-day volume change |
| WEIGHT_VOLATILITY | 0.20 | 21-day rolling std (INVERTED before passing in) |
| WEIGHT_RELATIVE_STRENGTH | 0.15 | stock return minus domain median |
| WEIGHT_FINANCIAL_RATIO | 0.15 | trailingPE (INVERTED before passing in) |

## normalize_factor() Rules
- Cap ±3σ → Z-score (ddof=0, population std)
- std == 0 → all 0.0
- fewer than 2 non-None → all None

## compute_composite() Rules
- Exclude None factors
- Proportionally reweight remaining to sum to 1.0
- financial_ratio None is the NORMAL case — reweighting fires regularly

## scale_to_0_100() Rules
- min-max within peer group
- max == min → all 50.0

## rank_domain() Edge Cases
- Single stock → score=50.0, rank=1
- Empty → returns `{}`

## Pure Module Rule
- ranking_engine.py must NOT import: app.database, app.models, yfinance
- Only allowed: dataclasses, typing, numpy
