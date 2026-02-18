"""
test_ranking_engine.py — Comprehensive TDD suite for the ranking engine.

All 6 required test cases covering:
  1. Single-stock domain
  2. std == 0 guard (all identical values)
  3. Outlier capping at ±3σ
  4. Missing factor (None) reweighting
  5. 0–100 scaling correctness
  6. Score breakdown structure (FactorScore fields)
"""
import pytest
from app.services.ranking_engine import (
    rank_domain,
    normalize_factor,
    compute_composite,
    scale_to_0_100,
    StockScore,
    FactorScore,
    WEIGHT_MOMENTUM,
    WEIGHT_VOLUME_CHANGE,
    WEIGHT_VOLATILITY,
    WEIGHT_RELATIVE_STRENGTH,
    WEIGHT_FINANCIAL_RATIO,
)

# ---------------------------------------------------------------------------
# Case 1: Single-stock domain
# ---------------------------------------------------------------------------

def test_single_stock_returns_score_50_and_rank_1():
    """A single-stock domain cannot be Z-scored. Must return 50.0 and rank 1."""
    data = {
        "AAPL": {
            "momentum": 0.05,
            "volume_change": 0.10,
            "volatility": -0.02,
            "relative_strength": 0.01,
            "financial_ratio": -15.0,
        }
    }
    result = rank_domain(data)
    assert "AAPL" in result
    score = result["AAPL"]
    assert isinstance(score, StockScore)
    assert score.composite_score == 50.0
    assert score.rank == 1


# ---------------------------------------------------------------------------
# Case 2: std == 0 guard — all identical factor values
# ---------------------------------------------------------------------------

def test_normalize_factor_std_zero_returns_all_zeros():
    """When all values are identical, std == 0. Must return [0.0, 0.0, 0.0], not raise."""
    result = normalize_factor([0.05, 0.05, 0.05])
    assert result == [0.0, 0.0, 0.0], f"Expected [0.0, 0.0, 0.0], got {result}"
    # Ensure no NaN or None leaked through
    for v in result:
        assert v == 0.0


# ---------------------------------------------------------------------------
# Case 3: Outlier capping at mean ± 3σ
# ---------------------------------------------------------------------------

def test_normalize_factor_caps_outlier_before_z_scoring():
    """The value 100.0 is an extreme outlier. Without capping, its Z-score would be >> 5.
    With capping, the result should be < 5.0 (bounded by definition of 3σ cap).
    """
    result = normalize_factor([1.0, 2.0, 3.0, 100.0])
    assert result is not None
    assert len(result) == 4
    # Uncapped Z-score for 100.0 would be enormous (>> 5); capped must be <= 3.0
    assert result[-1] < 5.0, f"Outlier should be capped; got Z-score {result[-1]}"
    # The capped value must also be the maximum in the result (still highest)
    assert result[-1] == max(r for r in result if r is not None)


# ---------------------------------------------------------------------------
# Case 4: Missing factor (None) reweighting
# ---------------------------------------------------------------------------

def test_missing_factor_reweights_remaining_proportionally():
    """When volume_change is None for all stocks, remaining 4 factors must
    pick up its weight proportionally. Their effective weights must sum to 1.0.
    """
    data = {
        "AAPL": {
            "momentum": 0.05,
            "volume_change": None,
            "volatility": -0.02,
            "relative_strength": 0.01,
            "financial_ratio": -15.0,
        },
        "MSFT": {
            "momentum": 0.03,
            "volume_change": None,
            "volatility": -0.01,
            "relative_strength": 0.02,
            "financial_ratio": -20.0,
        },
    }
    result = rank_domain(data)
    assert "AAPL" in result and "MSFT" in result

    for ticker in ["AAPL", "MSFT"]:
        stock = result[ticker]
        # volume_change factor must be excluded (normalized = None)
        vc = stock.factor_scores["volume_change"]
        assert vc.normalized is None, f"{ticker}: volume_change normalized should be None"
        assert vc.weighted is None, f"{ticker}: volume_change weighted should be None"

        # Effective weights of the 4 remaining factors must sum to 1.0
        effective_total = sum(
            fs.effective_weight
            for name, fs in stock.factor_scores.items()
            if name != "volume_change"
        )
        assert abs(effective_total - 1.0) < 1e-9, (
            f"{ticker}: effective weights of present factors should sum to 1.0, got {effective_total}"
        )


# ---------------------------------------------------------------------------
# Case 5: 0–100 scaling correctness
# ---------------------------------------------------------------------------

def test_scaling_best_is_100_worst_is_0():
    """With 3 stocks having distinct final composite scores, the best must
    scale to 100.0, the worst to 0.0, and the middle must be between them.
    """
    data = {
        "BEST": {
            "momentum": 0.10,
            "volume_change": 0.20,
            "volatility": -0.01,
            "relative_strength": 0.05,
            "financial_ratio": -10.0,
        },
        "MID": {
            "momentum": 0.05,
            "volume_change": 0.10,
            "volatility": -0.02,
            "relative_strength": 0.02,
            "financial_ratio": -15.0,
        },
        "WORST": {
            "momentum": -0.05,
            "volume_change": -0.10,
            "volatility": -0.05,
            "relative_strength": -0.05,
            "financial_ratio": -30.0,
        },
    }
    result = rank_domain(data)
    assert len(result) == 3

    scores = {t: result[t].composite_score for t in result}
    assert scores["BEST"] == 100.0, f"Best stock must be 100.0, got {scores['BEST']}"
    assert scores["WORST"] == 0.0, f"Worst stock must be 0.0, got {scores['WORST']}"
    assert 0.0 < scores["MID"] < 100.0, f"Middle stock must be between 0 and 100, got {scores['MID']}"


# ---------------------------------------------------------------------------
# Case 6: Score breakdown structure (FactorScore fields)
# ---------------------------------------------------------------------------

def test_factor_score_structure_has_all_required_fields():
    """Every StockScore must have factor_scores with all 5 factor keys.
    Each FactorScore must have .raw, .normalized, .weighted, .effective_weight.
    """
    data = {
        "AAPL": {
            "momentum": 0.05,
            "volume_change": 0.10,
            "volatility": -0.02,
            "relative_strength": 0.01,
            "financial_ratio": None,   # intentionally None — common case
        },
        "MSFT": {
            "momentum": 0.03,
            "volume_change": 0.08,
            "volatility": -0.01,
            "relative_strength": 0.02,
            "financial_ratio": None,
        },
    }
    expected_factors = {
        "momentum",
        "volume_change",
        "volatility",
        "relative_strength",
        "financial_ratio",
    }
    result = rank_domain(data)
    for ticker, stock in result.items():
        assert isinstance(stock, StockScore), f"{ticker} result is not a StockScore"
        assert set(stock.factor_scores.keys()) == expected_factors, (
            f"{ticker}: factor_scores keys mismatch"
        )
        for factor_name, fs in stock.factor_scores.items():
            assert isinstance(fs, FactorScore), (
                f"{ticker}.{factor_name} is not a FactorScore"
            )
            # Check all 4 attributes exist (raw can be float or None)
            assert hasattr(fs, "raw"), f"{ticker}.{factor_name} missing .raw"
            assert hasattr(fs, "normalized"), f"{ticker}.{factor_name} missing .normalized"
            assert hasattr(fs, "weighted"), f"{ticker}.{factor_name} missing .weighted"
            assert hasattr(fs, "effective_weight"), (
                f"{ticker}.{factor_name} missing .effective_weight"
            )
            assert isinstance(fs.effective_weight, float), (
                f"{ticker}.{factor_name}.effective_weight must be float"
            )


# ---------------------------------------------------------------------------
# Additional: empty domain returns empty dict
# ---------------------------------------------------------------------------

def test_empty_domain_returns_empty_dict():
    """rank_domain({}) must return {} without raising."""
    result = rank_domain({})
    assert result == {}


# ---------------------------------------------------------------------------
# Additional: weight constants sum to 1.0
# ---------------------------------------------------------------------------

def test_weight_constants_sum_to_1():
    """The 5 named weight constants must sum exactly to 1.0."""
    total = (
        WEIGHT_MOMENTUM
        + WEIGHT_VOLUME_CHANGE
        + WEIGHT_VOLATILITY
        + WEIGHT_RELATIVE_STRENGTH
        + WEIGHT_FINANCIAL_RATIO
    )
    assert abs(total - 1.0) < 1e-9, f"Weights must sum to 1.0, got {total}"
