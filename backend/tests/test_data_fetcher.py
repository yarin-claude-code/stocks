"""
Tests for data_fetcher.py — yfinance batch fetch and validation.

All yfinance calls are mocked; no real network calls are made.
"""
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from app.services.data_fetcher import (
    SEED_TICKERS,
    fetch_all_stocks,
    validate_ticker_data,
)

# ---------------------------------------------------------------------------
# validate_ticker_data tests
# ---------------------------------------------------------------------------


def test_validate_ticker_data_valid():
    """Valid close and volume should return True."""
    assert validate_ticker_data("AAPL", 182.5, 55_000_000.0) is True


def test_validate_ticker_data_nan_close():
    """NaN close price should return False."""
    assert validate_ticker_data("BAD", float("nan"), 1_000.0) is False


def test_validate_ticker_data_nan_volume():
    """NaN volume should return False."""
    assert validate_ticker_data("BAD", 100.0, float("nan")) is False


def test_validate_ticker_data_zero_close():
    """Zero close price should return False."""
    assert validate_ticker_data("BAD", 0.0, 1_000.0) is False


def test_validate_ticker_data_negative_close():
    """Negative close price should return False."""
    assert validate_ticker_data("BAD", -5.0, 1_000.0) is False


def test_validate_ticker_data_zero_volume():
    """Zero volume should return False."""
    assert validate_ticker_data("BAD", 100.0, 0.0) is False


def test_validate_ticker_data_negative_volume():
    """Negative volume should return False."""
    assert validate_ticker_data("BAD", 100.0, -500.0) is False


# ---------------------------------------------------------------------------
# fetch_all_stocks tests
# ---------------------------------------------------------------------------


def test_fetch_all_stocks_empty_list():
    """Empty tickers list should return {} without calling yfinance."""
    result = fetch_all_stocks([])
    assert result == {}


def test_fetch_all_stocks_returns_dict_on_success():
    """fetch_all_stocks should return a dict keyed by ticker with close_price and volume."""
    tickers = ["AAPL", "MSFT"]

    # Build a realistic MultiIndex DataFrame that yf.download returns
    close_data = {"AAPL": [180.0, 182.5], "MSFT": [310.0, 315.0]}
    volume_data = {"AAPL": [50_000_000.0, 55_000_000.0], "MSFT": [20_000_000.0, 22_000_000.0]}

    close_df = pd.DataFrame(close_data)
    volume_df = pd.DataFrame(volume_data)

    mock_raw = MagicMock()
    mock_raw.__getitem__ = lambda self, key: close_df if key == "Close" else volume_df

    with patch("app.services.data_fetcher.yf.download", return_value=mock_raw):
        result = fetch_all_stocks(tickers)

    assert "AAPL" in result
    assert "MSFT" in result
    assert result["AAPL"]["close_price"] == pytest.approx(182.5)
    assert result["AAPL"]["volume"] == pytest.approx(55_000_000.0)
    assert result["MSFT"]["close_price"] == pytest.approx(315.0)
    assert result["MSFT"]["volume"] == pytest.approx(22_000_000.0)


def test_fetch_all_stocks_no_exception_on_yfinance_failure():
    """fetch_all_stocks must return {} and never raise when yfinance throws."""
    with patch("app.services.data_fetcher.yf.download", side_effect=Exception("network error")):
        result = fetch_all_stocks(["AAPL"])

    assert result == {}


def test_fetch_all_stocks_skips_invalid_tickers():
    """Tickers that fail validation (NaN close) should be excluded from the result."""
    tickers = ["AAPL", "BAD"]

    close_data = {"AAPL": [180.0, 182.5], "BAD": [float("nan"), float("nan")]}
    volume_data = {"AAPL": [50_000_000.0, 55_000_000.0], "BAD": [1_000.0, 1_000.0]}

    close_df = pd.DataFrame(close_data)
    volume_df = pd.DataFrame(volume_data)

    mock_raw = MagicMock()
    mock_raw.__getitem__ = lambda self, key: close_df if key == "Close" else volume_df

    with patch("app.services.data_fetcher.yf.download", return_value=mock_raw):
        result = fetch_all_stocks(tickers)

    assert "AAPL" in result
    assert "BAD" not in result


def test_fetch_all_stocks_uses_single_batch_download():
    """yf.download must be called exactly once (batch), never in a per-ticker loop."""
    tickers = ["AAPL", "MSFT", "NVDA"]

    close_data = {t: [100.0, 110.0] for t in tickers}
    volume_data = {t: [1_000_000.0, 1_100_000.0] for t in tickers}

    close_df = pd.DataFrame(close_data)
    volume_df = pd.DataFrame(volume_data)

    mock_raw = MagicMock()
    mock_raw.__getitem__ = lambda self, key: close_df if key == "Close" else volume_df

    with patch("app.services.data_fetcher.yf.download", return_value=mock_raw) as mock_dl:
        fetch_all_stocks(tickers)

    assert mock_dl.call_count == 1, "yf.download should be called exactly once (batch)"


def test_seed_tickers_is_list_of_strings():
    """SEED_TICKERS must be a non-empty list of strings."""
    assert isinstance(SEED_TICKERS, list)
    assert len(SEED_TICKERS) > 0
    assert all(isinstance(t, str) for t in SEED_TICKERS)


def test_fetch_all_stocks_default_uses_seed_tickers():
    """Calling fetch_all_stocks() with no args should use SEED_TICKERS."""
    close_data = {t: [100.0, 110.0] for t in SEED_TICKERS}
    volume_data = {t: [1_000_000.0, 1_100_000.0] for t in SEED_TICKERS}

    close_df = pd.DataFrame(close_data)
    volume_df = pd.DataFrame(volume_data)

    mock_raw = MagicMock()
    mock_raw.__getitem__ = lambda self, key: close_df if key == "Close" else volume_df

    with patch("app.services.data_fetcher.yf.download", return_value=mock_raw) as mock_dl:
        fetch_all_stocks()

    call_args = mock_dl.call_args
    passed_tickers = call_args[0][0]  # first positional arg
    assert passed_tickers == SEED_TICKERS
