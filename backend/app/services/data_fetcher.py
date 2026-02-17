"""
data_fetcher.py — yfinance batch data fetcher and validation.

Fetches the most recent close price and volume for a list of tickers
using a single yf.download() batch call. Falls back to an empty dict
on any yfinance error (never raises to the caller).
"""
import math
import logging
import yfinance as yf

logger = logging.getLogger(__name__)

SEED_TICKERS = ["AAPL", "MSFT", "NVDA", "AMD", "GOOGL", "TSLA", "RIVN", "JPM", "GS"]


def validate_ticker_data(ticker: str, close: float, volume: float) -> bool:
    """Return True only when close and volume are finite positive numbers."""
    if math.isnan(close) or close <= 0:
        return False
    if math.isnan(volume) or volume <= 0:
        return False
    return True


def fetch_all_stocks(tickers: list[str] | None = None) -> dict[str, dict]:
    """Batch-download the most recent day's close/volume for *tickers*.

    Parameters
    ----------
    tickers:
        List of ticker symbols. Defaults to SEED_TICKERS. An empty list
        returns {} immediately without calling yfinance.

    Returns
    -------
    dict mapping ticker -> {"close_price": float, "volume": float}
    for every ticker that passes validate_ticker_data().
    Returns {} on any yfinance error (never raises).
    """
    if tickers is None:
        tickers = SEED_TICKERS
    if not tickers:
        return {}

    try:
        raw = yf.download(
            tickers,
            period="2d",
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=True,
        )
        result: dict[str, dict] = {}
        for ticker in tickers:
            try:
                close = float(raw["Close"][ticker].iloc[-1])
                volume = float(raw["Volume"][ticker].iloc[-1])
                if validate_ticker_data(ticker, close, volume):
                    result[ticker] = {"close_price": close, "volume": volume}
                else:
                    logger.warning(
                        "Ticker %s failed validation (close=%s, volume=%s)",
                        ticker,
                        close,
                        volume,
                    )
            except Exception as exc:
                logger.warning("Could not extract data for %s: %s", ticker, exc)
        return result
    except Exception as exc:
        logger.error("yfinance batch download failed: %s", exc)
        return {}
