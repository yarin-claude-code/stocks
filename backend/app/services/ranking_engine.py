"""
ranking_engine.py — Pure quantitative stock ranking engine.

This module is intentionally isolated: NO imports from app.database,
app.models, or any I/O library (yfinance, sqlalchemy, etc.).
Only stdlib + numpy are permitted here.

Pipeline:
  raw values -> normalize_factor() -> compute_composite() -> scale_to_0_100() -> rank_domain()

Factor weights (sum to 1.0):
  momentum          0.30  — strongest short-term price signal
  volume_change     0.20  — confirms momentum with liquidity evidence
  volatility        0.20  — inverted before passing in; penalises instability
  relative_strength 0.15  — stock return minus domain median; pure peer comparison
  financial_ratio   0.15  — trailingPE inverted before passing in; cheaper = higher score
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

# ---------------------------------------------------------------------------
# Named weight constants — MUST sum to 1.0
# ---------------------------------------------------------------------------

WEIGHT_MOMENTUM: float = 0.30
WEIGHT_VOLUME_CHANGE: float = 0.20
WEIGHT_VOLATILITY: float = 0.20
WEIGHT_RELATIVE_STRENGTH: float = 0.15
WEIGHT_FINANCIAL_RATIO: float = 0.15

_FACTOR_WEIGHTS: dict[str, float] = {
    "momentum": WEIGHT_MOMENTUM,
    "volume_change": WEIGHT_VOLUME_CHANGE,
    "volatility": WEIGHT_VOLATILITY,
    "relative_strength": WEIGHT_RELATIVE_STRENGTH,
    "financial_ratio": WEIGHT_FINANCIAL_RATIO,
}

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class FactorScore:
    """Per-factor breakdown stored inside StockScore."""

    raw: Optional[float]
    normalized: Optional[float]   # None when factor excluded (missing raw)
    weighted: Optional[float]     # None when factor excluded
    effective_weight: float       # Actual weight used after proportional reweighting


@dataclass
class StockScore:
    """Final ranking result for a single ticker within its domain."""

    ticker: str
    composite_score: float        # 0–100 within peer domain
    rank: int                     # 1 = best
    factor_scores: dict[str, FactorScore]


# ---------------------------------------------------------------------------
# normalize_factor
# ---------------------------------------------------------------------------


def normalize_factor(values: list[Optional[float]]) -> list[Optional[float]]:
    """Cap ±3σ then Z-score a list of raw factor values.

    Parameters
    ----------
    values:
        Raw factor values; None entries represent missing data for a ticker.

    Returns
    -------
    list of Optional[float]:
        Z-scored values; None inputs preserved as None outputs.
        Returns all-None if fewer than 2 non-None values exist.
        Returns all-zero if population std == 0 (all identical values).
    """
    non_none_indices = [i for i, v in enumerate(values) if v is not None]

    # Cannot normalize fewer than 2 data points
    if len(non_none_indices) < 2:
        return [None] * len(values)

    non_none_vals = np.array([values[i] for i in non_none_indices], dtype=float)

    mean = float(np.mean(non_none_vals))
    std = float(np.std(non_none_vals, ddof=0))  # population std

    # std == 0 guard — all values identical, Z-score is 0 for all.
    # Use epsilon tolerance because floating-point std of identical values is
    # not always exactly 0.0 (e.g. np.std([0.05, 0.05, 0.05]) ~ 6.9e-18).
    if std < 1e-12:
        result: list[Optional[float]] = [None] * len(values)
        for i in non_none_indices:
            result[i] = 0.0
        return result

    # Cap at mean ± 3*std BEFORE Z-scoring
    lower = mean - 3.0 * std
    upper = mean + 3.0 * std
    capped = np.clip(non_none_vals, lower, upper)

    # Z-score the capped values (use capped mean/std for robustness — per spec, cap then Z)
    z_scores = (capped - mean) / std

    result = [None] * len(values)
    for idx, i in enumerate(non_none_indices):
        result[i] = float(z_scores[idx])
    return result


# ---------------------------------------------------------------------------
# compute_composite
# ---------------------------------------------------------------------------


def compute_composite(
    normalized_dict: dict[str, Optional[float]],
    weights: dict[str, float],
) -> tuple[float, dict[str, float]]:
    """Weighted sum of normalized factor scores with proportional reweighting.

    Factors whose normalized value is None are excluded. The remaining factors'
    base weights are scaled proportionally so they sum to 1.0.

    Parameters
    ----------
    normalized_dict:
        {factor_name: z_score_or_None}
    weights:
        {factor_name: base_weight}

    Returns
    -------
    (weighted_sum, {factor_name: effective_weight_used})
    If ALL factors are None, returns (0.0, {}).
    """
    present = {
        name: z
        for name, z in normalized_dict.items()
        if z is not None
    }

    if not present:
        return 0.0, {}

    total_base_weight = sum(weights[name] for name in present if name in weights)

    if total_base_weight == 0.0:
        # Distribute evenly if somehow all base weights are zero
        effective_weights = {name: 1.0 / len(present) for name in present}
    else:
        effective_weights = {
            name: weights[name] / total_base_weight
            for name in present
            if name in weights
        }

    weighted_sum = sum(z * effective_weights[name] for name, z in present.items())
    return float(weighted_sum), effective_weights


# ---------------------------------------------------------------------------
# scale_to_0_100
# ---------------------------------------------------------------------------


def scale_to_0_100(composite_scores: dict[str, float]) -> dict[str, float]:
    """Min-max scale composite scores to the 0–100 range within the peer group.

    Parameters
    ----------
    composite_scores:
        {ticker: composite_weighted_sum}

    Returns
    -------
    {ticker: scaled_score_0_to_100}
    If max == min (all identical or single stock), all scores = 50.0.
    """
    if not composite_scores:
        return {}

    min_val = min(composite_scores.values())
    max_val = max(composite_scores.values())

    if max_val == min_val:
        return {ticker: 50.0 for ticker in composite_scores}

    return {
        ticker: (v - min_val) / (max_val - min_val) * 100.0
        for ticker, v in composite_scores.items()
    }


# ---------------------------------------------------------------------------
# rank_domain
# ---------------------------------------------------------------------------


def rank_domain(
    stocks_data: dict[str, dict[str, Optional[float]]],
) -> dict[str, StockScore]:
    """Full ranking pipeline for all stocks in a single domain.

    Parameters
    ----------
    stocks_data:
        {ticker: {factor_name: raw_value_or_None}}

    Returns
    -------
    {ticker: StockScore} — ranked 1 = highest composite_score.
    Empty input -> {}.
    Single stock -> composite_score=50.0, rank=1 (Z-score not run).
    """
    if not stocks_data:
        return {}

    tickers = list(stocks_data.keys())
    factor_names = list(_FACTOR_WEIGHTS.keys())

    # ------------------------------------------------------------------
    # Single-stock shortcut — cannot normalize, return 50.0 / rank 1
    # ------------------------------------------------------------------
    if len(tickers) == 1:
        ticker = tickers[0]
        raw_data = stocks_data[ticker]
        factor_scores: dict[str, FactorScore] = {}
        for fname in factor_names:
            raw = raw_data.get(fname)
            factor_scores[fname] = FactorScore(
                raw=raw,
                normalized=None,
                weighted=None,
                effective_weight=_FACTOR_WEIGHTS[fname],
            )
        return {
            ticker: StockScore(
                ticker=ticker,
                composite_score=50.0,
                rank=1,
                factor_scores=factor_scores,
            )
        }

    # ------------------------------------------------------------------
    # Multi-stock pipeline
    # ------------------------------------------------------------------

    # Step 1: Normalize each factor across all tickers
    normalized_by_factor: dict[str, list[Optional[float]]] = {}
    for fname in factor_names:
        raw_values = [stocks_data[t].get(fname) for t in tickers]
        normalized_by_factor[fname] = normalize_factor(raw_values)

    # Step 2: Compute composite score per ticker
    composite_scores: dict[str, float] = {}
    per_ticker_normalized: dict[str, dict[str, Optional[float]]] = {}
    per_ticker_effective_weights: dict[str, dict[str, float]] = {}

    for i, ticker in enumerate(tickers):
        normalized_dict = {
            fname: normalized_by_factor[fname][i]
            for fname in factor_names
        }
        per_ticker_normalized[ticker] = normalized_dict

        weighted_sum, effective_weights = compute_composite(
            normalized_dict, _FACTOR_WEIGHTS
        )
        composite_scores[ticker] = weighted_sum
        per_ticker_effective_weights[ticker] = effective_weights

    # Step 3: Scale to 0–100
    scaled = scale_to_0_100(composite_scores)

    # Step 4: Assign ranks (1 = highest score)
    sorted_tickers = sorted(scaled, key=lambda t: scaled[t], reverse=True)
    ranks: dict[str, int] = {t: idx + 1 for idx, t in enumerate(sorted_tickers)}

    # Step 5: Build StockScore objects with full FactorScore breakdown
    results: dict[str, StockScore] = {}
    for ticker in tickers:
        effective_weights = per_ticker_effective_weights[ticker]
        norm_dict = per_ticker_normalized[ticker]
        factor_scores = {}

        for fname in factor_names:
            raw = stocks_data[ticker].get(fname)
            normalized = norm_dict[fname]
            eff_weight = effective_weights.get(fname, 0.0)

            if normalized is not None:
                weighted = normalized * eff_weight
            else:
                weighted = None

            factor_scores[fname] = FactorScore(
                raw=raw,
                normalized=normalized,
                weighted=weighted,
                effective_weight=eff_weight,
            )

        results[ticker] = StockScore(
            ticker=ticker,
            composite_score=scaled[ticker],
            rank=ranks[ticker],
            factor_scores=factor_scores,
        )

    return results
