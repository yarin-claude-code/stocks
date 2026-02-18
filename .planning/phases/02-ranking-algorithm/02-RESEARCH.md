# Phase 2: Ranking Algorithm - Research

**Researched:** 2026-02-18
**Domain:** Statistical normalization, financial factor computation, weighted scoring, pure-Python service module design, pytest edge-case testing
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
User has explicitly delegated ALL implementation decisions to Claude. There are no locked external library choices or structural mandates beyond the phase boundary description:
- Module lives at `backend/app/services/ranking_engine.py`
- Z-score normalization with ±3 std dev outlier capping
- Five factors: price momentum, volume change, volatility, sector relative strength, financial ratios
- Weighted composite score on 0–100 scale
- Peer-domain ranking (not global)
- Per-factor score breakdown data structure
- Comprehensive pytest test suite

### Claude's Discretion
All of the following are delegated to Claude:
- **Factor weights** — Suggested starting point: price momentum 30%, volume change 20%, volatility 20%, sector relative strength 15%, financial ratios 15%. Weights must sum to 1.0 and be defined as named constants.
- **Score interpretation** — Scores are relative within the peer domain on a given run. Score of 100 = best in domain that day, 0 = worst. Scores reset each calculation cycle.
- **Peer group edge cases** — 1 stock in domain → score 50 (neutral midpoint). 2+ stocks → normal Z-score.
- **Missing data policy** — If a factor value is NaN/missing, exclude that factor and reweight remaining factors proportionally. Never silently score 0 for missing data.
- **Score breakdown structure** — Return a dict/dataclass with `composite_score`, `rank`, `factor_scores: {factor_name: {raw, normalized, weighted}}`.

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| ALGO-01 | App calculates composite score using 5 factors: price momentum, volume change, volatility, sector relative strength, financial ratios | All 5 factors are computable from yfinance `download()` + `Ticker.info`; factor calculation patterns documented in Code Examples |
| ALGO-02 | App normalizes all factors via z-score normalization with outlier capping (±3 std dev) | `numpy` mean/std + `numpy.clip` is the standard pattern; pure Python, no extra dependency |
| ALGO-03 | App produces a single weighted score (0–100 scale) per stock | Weighted sum of normalized factors → percentile rank → linear scale 0–100 within peer group |
| ALGO-04 | App displays the top 5 ranked stocks per selected domain | Ranking engine returns rank per stock in domain; API/UI layer in Phase 3 does the top-5 slice |
| ALGO-05 | App displays a single "Best Overall Investment Today" across all domains | Ranking engine output includes per-domain scores; cross-domain best = max composite score across all |
| ALGO-06 | App shows mathematical breakdown of how each stock's score was computed (per-factor contribution) | `StockScore` dataclass/dict includes `factor_scores` with `raw`, `normalized`, `weighted` per factor |
</phase_requirements>

---

## Summary

Phase 2 builds an isolated, stateless scoring module (`ranking_engine.py`) that takes a dict of stock data keyed by ticker and returns a dict of `StockScore` objects. The module never touches the database or yfinance directly — the scheduler or a caller provides pre-fetched data, and the engine returns scores. This makes the engine fully unit-testable with plain Python dicts.

The five scoring factors are computable from two data sources: (1) `yf.download()` historical price and volume series already being fetched by the scheduler, and (2) `yf.Ticker(ticker).info` for fundamental ratios (P/E, P/B). A critical finding is that `ticker.info` fields are unreliable — `pegRatio` broke industry-wide in June 2025, and `trailingPE`/`priceToBook` can return `None` silently. The missing-data reweighting policy (delegated to Claude's discretion) is therefore not an edge case — it is a core execution path that will run regularly in production.

The normalization pipeline is: (1) for each factor, cap raw values to `[mean - 3σ, mean + 3σ]`, (2) compute Z-score for each capped value, (3) multiply by factor weight with proportional reweighting for missing factors, (4) map the summed weighted Z-scores to a 0–100 scale using min-max scaling within the peer group. Z-score computation is done with pure NumPy (no scipy dependency needed). The 0–100 final scale uses pandas `rank(pct=True)` or simple min-max within the peer group.

**Primary recommendation:** Use `numpy` for Z-score and capping, `dataclasses.dataclass` for the return type, and `yf.Ticker.info.get()` with `None` fallback for fundamentals. Keep the entire engine as pure functions with no I/O — maximum testability.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| numpy | >=1.26 (already in pandas dep) | Z-score, std, mean, clip, pct_change computation | Standard numerical library; no scipy needed for this use case |
| pandas | >=2.2 (already in requirements.txt) | Rolling window for volatility, pct_change for momentum/volume | Already present; `.rolling().std()`, `.pct_change()` are the idiomatic approach |
| dataclasses | stdlib | `StockScore` return type with typed fields | No extra dependency; better than plain dict for IDE support and type safety |
| yfinance | >=1.0 (already in requirements.txt) | Source of historical data (via download) and fundamentals (via Ticker.info) | Already present; `Ticker.info.get()` for fundamentals with None fallback |
| pytest | >=8.0 (already in requirements.txt) | Test suite | Already present |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| math | stdlib | `math.isnan()`, `math.isfinite()` for scalar validation | Validating individual factor values before inclusion |
| typing | stdlib | `TypedDict` or type hints for factor input dicts | Clear API contracts for the engine's input format |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| numpy Z-score (manual) | scipy.stats.zscore | scipy adds a dependency; manual Z-score is 3 lines and more explicit for outlier capping |
| dataclass | TypedDict | TypedDict is dict-compatible but has no default values or methods; dataclass is better for this structured return |
| pandas rank(pct=True) | manual min-max | Both work; min-max is more explicit and easier to unit test with small groups |

**No new installation needed** — all dependencies already in `requirements.txt`.

---

## Architecture Patterns

### Recommended Module Structure
```
backend/app/services/
├── data_fetcher.py        # Phase 1 — already exists
└── ranking_engine.py      # Phase 2 — new module

backend/tests/
├── test_data_fetcher.py   # Phase 1 — already exists
└── test_ranking_engine.py # Phase 2 — new test file
```

### Pattern 1: Pure Function Engine (No I/O)
**What:** The ranking engine accepts pre-fetched data as plain Python dicts and returns score objects. It never calls yfinance, the database, or any network resource.
**When to use:** Always. This is the testability-enabling constraint for this module.

```python
# backend/app/services/ranking_engine.py
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class FactorScore:
    raw: Optional[float]        # raw input value (None if missing)
    normalized: Optional[float] # Z-score after capping (None if missing)
    weighted: Optional[float]   # normalized * effective_weight (None if missing)
    effective_weight: float     # actual weight used after reweighting

@dataclass
class StockScore:
    ticker: str
    composite_score: float      # 0–100, relative within peer domain
    rank: int                   # 1 = best in domain
    factor_scores: dict[str, FactorScore]  # keyed by factor name

def rank_domain(stocks_data: dict[str, dict]) -> dict[str, StockScore]:
    """
    Rank all stocks in a single peer domain.

    Parameters
    ----------
    stocks_data : dict[str, dict]
        Mapping of ticker -> factor values dict.
        Factor values dict has keys: "momentum", "volume_change",
        "volatility", "relative_strength", "financial_ratio".
        Any value may be None/NaN if unavailable.

    Returns
    -------
    dict[str, StockScore] keyed by ticker
    """
    ...
```

### Pattern 2: Z-Score with ±3 Std Dev Outlier Capping
**What:** For each factor across all stocks in the peer group, cap raw values at mean ± 3σ, then compute Z-scores on the capped values.
**When to use:** Applied to every factor before weighting.

```python
import numpy as np

def normalize_factor(values: list[Optional[float]]) -> list[Optional[float]]:
    """
    Z-score normalize a list of factor values with ±3 std dev capping.
    None values are preserved as None (excluded from stats computation).

    Returns list of normalized values (None where input was None).
    """
    # Extract valid (non-None, non-NaN) values
    valid_indices = [i for i, v in enumerate(values)
                     if v is not None and not math.isnan(v)]
    if len(valid_indices) < 2:
        # Not enough data to normalize — return None for all
        return [None] * len(values)

    valid_vals = np.array([values[i] for i in valid_indices], dtype=float)
    mean = np.mean(valid_vals)
    std = np.std(valid_vals, ddof=0)  # population std, consistent across group

    if std == 0:
        # All values identical — Z-scores are all 0
        return [0.0 if i in valid_indices else None for i in range(len(values))]

    # Cap at ±3 std dev BEFORE computing Z-score
    lower = mean - 3 * std
    upper = mean + 3 * std

    result = [None] * len(values)
    for i in valid_indices:
        capped = np.clip(values[i], lower, upper)
        result[i] = float((capped - mean) / std)
    return result
```

### Pattern 3: Proportional Reweighting for Missing Factors
**What:** When a factor is missing (None) for a stock, redistribute that factor's weight proportionally among the remaining available factors.
**When to use:** Per-stock, after normalization. Each stock may have a different effective weight distribution.

```python
# Base weights — must sum to 1.0
WEIGHTS = {
    "momentum":          0.30,  # price momentum: strongest predictor of near-term returns
    "volume_change":     0.20,  # volume surge signals conviction behind price move
    "volatility":        0.20,  # lower volatility = more stable, less risky
    "relative_strength": 0.15,  # peer-group outperformance signal
    "financial_ratio":   0.15,  # fundamental valuation anchor
}

def compute_composite(normalized: dict[str, Optional[float]]) -> tuple[float, dict[str, float]]:
    """
    Returns (weighted_z_score, effective_weights_used).
    Reweights proportionally for any factor with normalized=None.
    """
    available = {k: v for k, v in normalized.items() if v is not None}
    if not available:
        return 0.0, {}

    total_weight = sum(WEIGHTS[k] for k in available)
    effective_weights = {k: WEIGHTS[k] / total_weight for k in available}

    composite = sum(effective_weights[k] * available[k] for k in available)
    return composite, effective_weights
```

### Pattern 4: 0–100 Scaling Within Peer Group
**What:** Map raw weighted Z-scores to 0–100 using min-max scaling within the peer group. Min Z-score → 0, max → 100.
**When to use:** After all per-stock composites are computed. Applied only within the domain, never globally.

```python
def scale_to_0_100(composite_scores: dict[str, float]) -> dict[str, float]:
    """Min-max scale composite Z-scores to [0, 100] within a peer group."""
    if len(composite_scores) == 1:
        # Single stock — midpoint per policy
        return {ticker: 50.0 for ticker in composite_scores}

    values = list(composite_scores.values())
    min_val = min(values)
    max_val = max(values)

    if min_val == max_val:
        # All stocks scored identically
        return {ticker: 50.0 for ticker in composite_scores}

    return {
        ticker: 100.0 * (score - min_val) / (max_val - min_val)
        for ticker, score in composite_scores.items()
    }
```

### Pattern 5: Factor Computation from yfinance Data
**What:** Each of the 5 factors is computed from data the data_fetcher already provides or can provide.
**When to use:** In the scheduler's fetch_cycle, compute factors alongside raw price/volume, then pass to ranking_engine.

```
Factor                | Source                          | Computation
--------------------- | ------------------------------- | -----------
price_momentum        | yf.download() Close, period=6d  | pct_change(5) — 5-day return
volume_change         | yf.download() Volume, period=6d | pct_change(5) — 5-day volume change
volatility            | yf.download() Close, period=22d | rolling(21).std() of daily log returns
relative_strength     | yf.download() Close, period=6d  | stock 5-day return vs domain median return
financial_ratio       | yf.Ticker.info.get("trailingPE")| raw trailingPE; None if missing (reweight)
```

**Volatility interpretation note:** Volatility is a "lower is better" factor for ranking purposes (less volatile = less risky). The factor weight must invert the Z-score: higher normalized volatility = lower contribution. Implementation: multiply normalized volatility by -1 before applying weight, OR define volatility factor as `-1 * rolling_std`.

### Anti-Patterns to Avoid
- **Fetching data inside ranking_engine.py:** Never call yfinance or DB from the engine. The engine is pure computation.
- **Global ranking across domains:** Rankings are always within the peer domain. Cross-domain comparison (ALGO-05 "best overall") is done by the caller as `max(all_domain_scores, key=lambda s: s.composite_score)`.
- **Silently treating NaN as 0:** A missing P/E ratio scored as 0 creates a massive penalty. Always reweight proportionally.
- **Using population ddof=1 for tiny peer groups:** With 2-5 stocks, using ddof=1 (sample std) can produce unstable results. Use ddof=0 (population std) consistently — the group is the entire population for that domain.
- **Not inverting volatility:** Higher volatility = higher risk. If Z-scoring raw volatility, high volatility gets a high Z-score (good) unless explicitly inverted.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Z-score computation | Custom formula loop | `numpy` mean/std/clip | Already in pandas dep; handles float edge cases correctly |
| Rolling window std for volatility | Manual sliding window | `pandas.Series.rolling(21).std()` | pandas rolling handles edge cases, NaN propagation, and minimum periods |
| Min-max scaling | Custom formula | 4-line function using `min()`/`max()` | Simple enough to be explicit; sklearn `MinMaxScaler` is overkill for a list of 5-15 values |
| Factor weight normalization | Custom percentage logic | Python `sum()` + dict comprehension | 3 lines; no library needed |

**Key insight:** The ranking engine is simple enough that standard library + numpy + pandas covers everything. Resist the temptation to introduce sklearn, scipy, or MCDM libraries — they add complexity without benefit for a 5-factor weighted sum over 5-15 stocks.

---

## Common Pitfalls

### Pitfall 1: ticker.info Returning None Silently
**What goes wrong:** `yf.Ticker("AAPL").info["trailingPE"]` raises `KeyError` or returns `None` without warning. As of June 2025, `pegRatio` is confirmed broken for all major tickers; `trailingPE` and `priceToBook` are similarly unreliable.
**Why it happens:** Yahoo Finance's unofficial API changes field names or drops fields without notice. yfinance scrapes these fields and can't control availability.
**How to avoid:** Always use `.info.get("trailingPE")` (not dict bracket access). Validate the returned value with `math.isnan()` check after `None` check. Treat missing fundamentals as the default case, not the exception.
**Warning signs:** `KeyError` in scheduler logs, financial_ratio factor always at 0 or missing.

### Pitfall 2: Volatility Factor Direction Inversion
**What goes wrong:** After Z-score normalization, a stock with high volatility gets a high normalized score (many standard deviations above mean). Since we weight this positively, high-volatility stocks get boosted — the opposite of intent.
**Why it happens:** Z-scores are directionless; you must define what "high" means for each factor.
**How to avoid:** Document each factor's direction. For volatility: multiply the raw value by `-1` before normalization so that high volatility → low raw value → low Z-score → low contribution.
**Warning signs:** Very volatile stocks (RIVN, AMD) consistently ranking first; stable blue chips (AAPL, MSFT) consistently last.

### Pitfall 3: Division by Zero in Z-Score When std == 0
**What goes wrong:** If all stocks in a domain have identical factor values (e.g., a domain of 2 stocks where both have the same P/E ratio), std = 0 → ZeroDivisionError.
**Why it happens:** Small peer groups (2-3 stocks) are common in the seed data (EV domain has 2 stocks: TSLA, RIVN).
**How to avoid:** Check `if std == 0` before dividing. When std is 0, all Z-scores are 0 for that factor. This is handled in `normalize_factor()` above.
**Warning signs:** `ZeroDivisionError` in tests with identical values, or NaN Z-scores.

### Pitfall 4: Single-Stock Domain Scoring
**What goes wrong:** A domain with 1 stock has no peers to compare against. Z-score is undefined (std of a single value is 0 or NaN depending on ddof). Min-max scaling is undefined (max == min).
**Why it happens:** Current seed data has this risk if domains are filtered by available data.
**How to avoid:** Early-exit check: if `len(stocks_data) == 1`, return score=50, rank=1 without normalization. This is the defined policy in CONTEXT.md.
**Warning signs:** NaN composite scores, rank=0 or undefined rank for single-stock domains.

### Pitfall 5: Inconsistent ddof in std Computation
**What goes wrong:** numpy's `np.std()` defaults to `ddof=0` (population) but `pd.Series.std()` defaults to `ddof=1` (sample). Mixing these in tests vs. production code causes subtly different Z-scores.
**Why it happens:** numpy and pandas have different defaults for historical/statistical reasons.
**How to avoid:** Explicitly pass `ddof=0` everywhere. Use `np.std(values, ddof=0)` and document the choice.
**Warning signs:** Test assertions pass individually but fail when pandas is used in one place and numpy in another.

### Pitfall 6: Rank Assignment Ties
**What goes wrong:** Two stocks with identical composite scores need a defined tie-breaking rule. Python's default `sorted()` is not stable across factor changes.
**Why it happens:** Rounding or identical raw data produces tied composite scores.
**How to avoid:** Use `sorted(scores.items(), key=lambda x: (-x[1].composite_score, x[0]))` — sort by score descending, then ticker alphabetically for deterministic ties.
**Warning signs:** Rank order differs between runs with same input data.

---

## Code Examples

Verified patterns assembled from official NumPy/pandas docs and confirmed research:

### Complete normalize_factor Function
```python
# backend/app/services/ranking_engine.py
import math
import numpy as np
from typing import Optional

def normalize_factor(values: list[Optional[float]]) -> list[Optional[float]]:
    """
    Z-score normalize with ±3 std dev outlier capping.
    None/NaN values are preserved as None (excluded from statistics).
    Uses population std (ddof=0) for consistency with small groups.
    """
    valid_indices = [
        i for i, v in enumerate(values)
        if v is not None and not math.isnan(v) and math.isfinite(v)
    ]
    if len(valid_indices) < 2:
        return [None] * len(values)

    valid_vals = np.array([values[i] for i in valid_indices], dtype=float)
    mean = float(np.mean(valid_vals))
    std = float(np.std(valid_vals, ddof=0))

    if std == 0.0:
        return [0.0 if i in set(valid_indices) else None for i in range(len(values))]

    lower = mean - 3.0 * std
    upper = mean + 3.0 * std

    result: list[Optional[float]] = [None] * len(values)
    for i in valid_indices:
        capped = float(np.clip(values[i], lower, upper))
        result[i] = (capped - mean) / std
    return result
```

### Factor Computation from yfinance Data
```python
# Called in scheduler.py fetch_cycle, results passed to ranking_engine
import yfinance as yf
import numpy as np

def compute_factors_for_ticker(
    ticker: str,
    history: "pd.DataFrame",  # yf.download output for this ticker, 22+ day window
    all_histories: dict[str, "pd.DataFrame"],  # all tickers in domain, for relative strength
) -> dict[str, Optional[float]]:
    """
    Compute all 5 factor raw values for a single ticker.
    Returns None for any factor that cannot be computed.
    """
    factors: dict[str, Optional[float]] = {}

    # Factor 1: Price Momentum — 5-day return
    try:
        close = history["Close"].dropna()
        factors["momentum"] = float(close.pct_change(5).iloc[-1]) if len(close) >= 6 else None
    except Exception:
        factors["momentum"] = None

    # Factor 2: Volume Change — 5-day volume % change
    try:
        volume = history["Volume"].dropna()
        factors["volume_change"] = float(volume.pct_change(5).iloc[-1]) if len(volume) >= 6 else None
    except Exception:
        factors["volume_change"] = None

    # Factor 3: Volatility — 21-day rolling std of log returns (INVERTED: lower = better)
    try:
        close = history["Close"].dropna()
        log_returns = np.log(close / close.shift(1)).dropna()
        if len(log_returns) >= 5:
            vol = float(log_returns.rolling(min(21, len(log_returns))).std().iloc[-1])
            factors["volatility"] = -1.0 * vol  # invert: lower volatility = higher score
        else:
            factors["volatility"] = None
    except Exception:
        factors["volatility"] = None

    # Factor 4: Sector Relative Strength — stock 5-day return vs median domain return
    try:
        stock_momentum = factors.get("momentum")
        if stock_momentum is not None and all_histories:
            peer_momentums = []
            for peer_ticker, peer_hist in all_histories.items():
                if peer_ticker == ticker:
                    continue
                try:
                    peer_close = peer_hist["Close"].dropna()
                    peer_mom = float(peer_close.pct_change(5).iloc[-1])
                    if math.isfinite(peer_mom):
                        peer_momentums.append(peer_mom)
                except Exception:
                    pass
            if peer_momentums:
                median_domain = float(np.median(peer_momentums))
                factors["relative_strength"] = stock_momentum - median_domain
            else:
                factors["relative_strength"] = None
        else:
            factors["relative_strength"] = None
    except Exception:
        factors["relative_strength"] = None

    # Factor 5: Financial Ratio — trailing P/E (None is expected; triggers reweighting)
    try:
        info = yf.Ticker(ticker).info
        pe = info.get("trailingPE")
        if pe is not None and math.isfinite(float(pe)) and float(pe) > 0:
            # Invert PE: lower PE = cheaper stock = higher score
            factors["financial_ratio"] = -1.0 * float(pe)
        else:
            factors["financial_ratio"] = None
    except Exception:
        factors["financial_ratio"] = None

    return factors
```

### Core rank_domain Function Skeleton
```python
# backend/app/services/ranking_engine.py

FACTOR_NAMES = ["momentum", "volume_change", "volatility", "relative_strength", "financial_ratio"]

# Weights — must sum to 1.0
# Rationale:
#   momentum (0.30): strongest near-term price predictor; most responsive to current conditions
#   volume_change (0.20): confirms price moves with conviction; surge = institutional interest
#   volatility (0.20): lower volatility reduces tail risk; important for recommendation quality
#   relative_strength (0.15): within-peer outperformance is a reliable selection signal
#   financial_ratio (0.15): fundamental anchor; down-weighted due to yfinance unreliability
WEIGHTS = {
    "momentum":          0.30,
    "volume_change":     0.20,
    "volatility":        0.20,
    "relative_strength": 0.15,
    "financial_ratio":   0.15,
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Weights must sum to 1.0"


def rank_domain(stocks_data: dict[str, dict[str, Optional[float]]]) -> dict[str, StockScore]:
    """
    Rank all stocks in a peer domain.

    stocks_data: {ticker: {factor_name: raw_value_or_None}}
    Returns: {ticker: StockScore}
    """
    tickers = list(stocks_data.keys())

    # Edge case: single stock
    if len(tickers) == 1:
        ticker = tickers[0]
        factor_scores = {
            f: FactorScore(raw=stocks_data[ticker].get(f), normalized=None,
                           weighted=None, effective_weight=WEIGHTS[f])
            for f in FACTOR_NAMES
        }
        return {ticker: StockScore(ticker=ticker, composite_score=50.0,
                                    rank=1, factor_scores=factor_scores)}

    # Normalize each factor across all stocks in domain
    normalized: dict[str, list[Optional[float]]] = {}
    for factor in FACTOR_NAMES:
        raw_values = [stocks_data[t].get(factor) for t in tickers]
        normalized[factor] = normalize_factor(raw_values)

    # Compute composite Z-score per stock with proportional reweighting
    composite_z: dict[str, float] = {}
    effective_weights_per_stock: dict[str, dict[str, float]] = {}

    for idx, ticker in enumerate(tickers):
        norm_vals = {f: normalized[f][idx] for f in FACTOR_NAMES}
        composite, eff_weights = compute_composite(norm_vals)
        composite_z[ticker] = composite
        effective_weights_per_stock[ticker] = eff_weights

    # Scale to 0–100 within peer group
    scaled = scale_to_0_100(composite_z)

    # Assign ranks (1 = highest score)
    ranked = sorted(tickers, key=lambda t: (-scaled[t], t))
    ranks = {ticker: i + 1 for i, ticker in enumerate(ranked)}

    # Build StockScore objects
    result: dict[str, StockScore] = {}
    for idx, ticker in enumerate(tickers):
        eff_w = effective_weights_per_stock[ticker]
        factor_scores = {}
        for factor in FACTOR_NAMES:
            raw = stocks_data[ticker].get(factor)
            norm = normalized[factor][idx]
            w = eff_w.get(factor, 0.0)
            weighted = norm * w if norm is not None else None
            factor_scores[factor] = FactorScore(
                raw=raw, normalized=norm, weighted=weighted, effective_weight=w
            )
        result[ticker] = StockScore(
            ticker=ticker,
            composite_score=round(scaled[ticker], 4),
            rank=ranks[ticker],
            factor_scores=factor_scores,
        )

    return result
```

### Test Patterns for Edge Cases
```python
# backend/tests/test_ranking_engine.py
import math
import pytest
from app.services.ranking_engine import rank_domain, normalize_factor, WEIGHTS

class TestNormalizeFactor:
    def test_normal_case(self):
        result = normalize_factor([10.0, 20.0, 30.0])
        assert result[0] < 0        # below mean
        assert result[2] > 0        # above mean
        assert abs(result[1]) < 0.1 # near mean

    def test_single_value_returns_none_list(self):
        result = normalize_factor([42.0])
        assert result == [None]

    def test_none_values_preserved(self):
        result = normalize_factor([10.0, None, 30.0])
        assert result[1] is None
        assert result[0] is not None
        assert result[2] is not None

    def test_nan_values_preserved(self):
        result = normalize_factor([10.0, float("nan"), 30.0])
        assert result[1] is None

    def test_all_identical_values_return_zero(self):
        result = normalize_factor([5.0, 5.0, 5.0])
        assert result == [0.0, 0.0, 0.0]

    def test_outlier_capping(self):
        # Value 1000 is a clear outlier; after capping it should not dominate
        result = normalize_factor([10.0, 12.0, 11.0, 1000.0])
        # The capped outlier's Z-score should not be massively higher than others
        assert result[3] is not None
        assert result[3] <= 3.0  # capped at 3σ

    @pytest.mark.parametrize("values,expected_nones", [
        ([None, None], 2),
        ([float("nan"), float("nan")], 2),
        ([None, 10.0], 2),  # only 1 valid — insufficient for normalization
    ])
    def test_insufficient_valid_values(self, values, expected_nones):
        result = normalize_factor(values)
        assert result.count(None) == expected_nones


class TestRankDomain:
    def test_single_stock_returns_score_50(self):
        data = {"AAPL": {"momentum": 0.05, "volume_change": 0.1,
                          "volatility": -0.01, "relative_strength": 0.02,
                          "financial_ratio": -25.0}}
        result = rank_domain(data)
        assert result["AAPL"].composite_score == 50.0
        assert result["AAPL"].rank == 1

    def test_better_stock_gets_higher_score(self):
        good = {"momentum": 0.10, "volume_change": 0.20,
                "volatility": -0.005, "relative_strength": 0.05, "financial_ratio": -15.0}
        bad = {"momentum": -0.05, "volume_change": -0.10,
               "volatility": -0.05, "relative_strength": -0.03, "financial_ratio": -50.0}
        result = rank_domain({"GOOD": good, "BAD": bad})
        assert result["GOOD"].composite_score > result["BAD"].composite_score
        assert result["GOOD"].rank == 1
        assert result["BAD"].rank == 2

    def test_missing_factor_triggers_reweighting(self):
        # Stock with missing financial_ratio should still get a valid score
        data = {
            "A": {"momentum": 0.05, "volume_change": 0.1,
                  "volatility": -0.01, "relative_strength": 0.02, "financial_ratio": None},
            "B": {"momentum": -0.02, "volume_change": 0.05,
                  "volatility": -0.02, "relative_strength": -0.01, "financial_ratio": None},
        }
        result = rank_domain(data)
        for ticker in ["A", "B"]:
            score = result[ticker]
            assert 0.0 <= score.composite_score <= 100.0
            fr = score.factor_scores["financial_ratio"]
            assert fr.effective_weight == 0.0  # reweighted away

    def test_all_missing_one_factor_reweights_others_to_sum_1(self):
        data = {
            "A": {"momentum": 0.05, "volume_change": 0.1,
                  "volatility": -0.01, "relative_strength": 0.02, "financial_ratio": None},
            "B": {"momentum": -0.02, "volume_change": 0.05,
                  "volatility": -0.02, "relative_strength": -0.01, "financial_ratio": None},
        }
        result = rank_domain(data)
        for ticker in result:
            eff_weights = [fs.effective_weight
                           for fs in result[ticker].factor_scores.values()]
            assert abs(sum(eff_weights) - 1.0) < 1e-9 or abs(sum(eff_weights)) < 1e-9

    def test_scores_are_0_to_100(self):
        data = {t: {"momentum": v, "volume_change": v, "volatility": -v,
                     "relative_strength": v, "financial_ratio": -v}
                for t, v in [("A", 0.10), ("B", 0.05), ("C", -0.02), ("D", -0.08)]}
        result = rank_domain(data)
        scores = [s.composite_score for s in result.values()]
        assert min(scores) >= 0.0
        assert max(scores) <= 100.0
        assert max(scores) == pytest.approx(100.0)
        assert min(scores) == pytest.approx(0.0)

    def test_factor_score_breakdown_present(self):
        data = {
            "A": {"momentum": 0.05, "volume_change": 0.1,
                  "volatility": -0.01, "relative_strength": 0.02, "financial_ratio": -20.0},
            "B": {"momentum": -0.02, "volume_change": 0.05,
                  "volatility": -0.02, "relative_strength": -0.01, "financial_ratio": -30.0},
        }
        result = rank_domain(data)
        for ticker, score in result.items():
            assert set(score.factor_scores.keys()) == {
                "momentum", "volume_change", "volatility",
                "relative_strength", "financial_ratio"
            }
            for factor, fs in score.factor_scores.items():
                assert hasattr(fs, "raw")
                assert hasattr(fs, "normalized")
                assert hasattr(fs, "weighted")
                assert hasattr(fs, "effective_weight")
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `ticker.history()` per stock for rolling data | `yf.download([...], period="30d")` batch | yfinance 1.x | Already adopted in Phase 1 |
| `scipy.stats.zscore` | `numpy` manual zscore (3 lines) | Ongoing | No new dependency; scipy overkill for this |
| Plain `dict` return from service functions | `@dataclass` with typed fields | Python 3.7+ | Better IDE support, easier assertions in tests |
| `pandas.DataFrame.rank(pct=True)` for scoring | Explicit min-max within peer group | — | More transparent, easier to unit test |
| `ticker.info["trailingPE"]` dict access | `ticker.info.get("trailingPE")` with None fallback | June 2025 (breakage) | CRITICAL: dict access raises KeyError on missing |

**Deprecated/outdated:**
- `pegRatio` from `ticker.info`: Confirmed broken since June 2025. Do not use as a factor.
- `pandas_datareader` for financial data: Dead, use yfinance directly.
- Using `scipy.stats.zscore` for this use case: Works, but adds a dependency for a 3-line operation.

---

## Open Questions

1. **Where in the pipeline are factors computed — in the scheduler or the ranking engine?**
   - What we know: The ranking engine should be pure (no I/O). Factor computation requires yfinance calls (for fundamentals) and historical price series (for momentum, volatility, etc.).
   - What's unclear: Should the scheduler compute all 5 factor raw values and pass them to the engine, OR should the engine receive raw OHLCV data and compute factors internally?
   - Recommendation: The scheduler computes factor raw values and passes them in. This keeps the engine truly pure. The data_fetcher module may need a `compute_factors()` companion function, or a new `factor_computer.py` service. The planner should decide module boundaries here.

2. **How much historical data does yf.download need for factor computation?**
   - What we know: Momentum = 5-day return (need 6 days), volume change = 5-day change (need 6 days), volatility = 21-day rolling std (need ~22 days, but 5 is acceptable minimum).
   - Recommendation: Change `period="2d"` in the current `fetch_all_stocks()` to `period="30d"` for the ranking cycle. The 2-day window only works for the current close/volume data — insufficient for momentum and volatility.

3. **Financial ratio: P/E only, or also P/B?**
   - What we know: `trailingPE` is more reliably populated than `priceToBook`. `pegRatio` is broken since June 2025. Both `trailingPE` and `priceToBook` can be None.
   - Recommendation: Use `trailingPE` as the primary financial ratio factor. It has the widest availability and is most commonly interpreted by retail investors (aligns with product's explainability goal). The reweighting policy handles cases where it's missing.

4. **Should Phase 2 extend the ScoreSnapshot model or leave DB changes to Phase 3?**
   - What we know: Phase 2 scope explicitly excludes DB storage — "Storing scores to DB and exposing via API are in Phase 3."
   - Recommendation: Phase 2 builds and tests the engine in isolation. The planner should not include any Alembic migration or DB interaction tasks in Phase 2.

---

## Sources

### Primary (HIGH confidence)
- NumPy official docs — `numpy.std`, `numpy.clip`, `numpy.mean`: functions confirmed, ddof parameter behavior documented
- pandas official docs — `Series.pct_change()`, `Series.rolling().std()`: standard methods for momentum and volatility computation
- Python stdlib `dataclasses` module docs: `@dataclass`, field types confirmed

### Secondary (MEDIUM confidence)
- [SciPy v1.17.0 `zscore` docs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.zscore.html) — confirmed scipy approach, used as reference for equivalent numpy implementation
- [Spot Intelligence — Z-Score Normalization (Feb 2025)](https://spotintelligence.com/2025/02/14/z-score-normalization/) — outlier capping at ±3σ confirmed as industry standard
- [yfinance GitHub Issue #2570](https://github.com/ranaroussi/yfinance/issues/2570) — pegRatio broken since June 2025, confirmed by multiple users
- [yfinance GitHub Issue #1639](https://github.com/ranaroussi/yfinance/issues/1639) — general ticker.info missing fields, confirmed pattern
- [StockCharts — Price Relative / Relative Strength](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/price-relative-relative-strength) — sector relative strength definition confirmed
- [pytest parametrize docs](https://docs.pytest.org/en/stable/how-to/parametrize.html) — edge case testing patterns confirmed

### Tertiary (LOW confidence — flagged for validation)
- Factor weight rationale (momentum=30%, etc.): Based on quantitative finance literature consensus, not empirically backtested for this specific use case. Weights are a starting point subject to tuning.
- Minimum rolling window of 5 days for volatility: Community practice, not formally validated for small peer groups.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries already in requirements.txt; numpy/pandas patterns from official docs
- Z-score normalization: HIGH — mathematical operation, verified against scipy docs
- Factor computation: MEDIUM-HIGH — patterns from yfinance docs + community; ticker.info unreliability confirmed via GitHub issues
- Factor weights: LOW — educated starting point, not backtested
- Pitfalls: HIGH — volatility inversion and ddof inconsistency are known mathematical facts; ticker.info issues confirmed via yfinance GitHub

**Research date:** 2026-02-18
**Valid until:** 2026-03-18 (30 days; yfinance reliability status may change; check GitHub issues if ticker.info fields break)
