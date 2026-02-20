"""
data_fetcher.py — yfinance batch data fetcher, validation, and factor computation.

Fetches the most recent close price and volume for a list of tickers
using a single yf.download() batch call. Falls back to an empty dict
on any yfinance error (never raises to the caller).

compute_factors_for_ticker() extracts all 5 raw factor values from a
30-day history DataFrame. Each factor is independently wrapped in
try/except so one failure does not block others.
"""
import math
import logging
import numpy as np
import yfinance as yf

logger = logging.getLogger(__name__)

SEED_TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMD", "GOOGL",
    "TSLA", "RIVN", "NIO", "LCID",
    "JPM", "GS", "BAC", "MS",
    "JNJ", "UNH", "PFE", "ABBV",
    "XOM", "CVX", "COP", "SLB",
    "AMZN", "WMT", "HD", "MCD",
    "TSM", "INTC", "QCOM", "AVGO",
    "LMT", "RTX", "NOC", "GD",
    "COIN", "PYPL", "SQ", "HOOD",
    "CAT", "DE", "HON", "UPS",
    "NFLX", "DIS", "SPOT", "PARA",
    "AMT", "PLD", "EQIX", "SPG",
]


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
            period="30d",
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


def compute_long_term_score(ticker: str) -> float | None:
    """Fetch 1-year daily history and compute a 0-100 long-term investment score.

    Combines three signals (each 0-100), equally weighted:
      - 1yr total return       (higher = better)
      - max drawdown           (less negative = better; inverted)
      - monthly consistency    (% of months with positive return)

    Returns None on any failure so the caller can store NULL gracefully.
    """
    try:
        hist = yf.download(
            ticker,
            period="1y",
            interval="1d",
            auto_adjust=True,
            progress=False,
        )
        if hist.empty or len(hist) < 20:
            return None

        close = hist["Close"].squeeze().dropna()
        if len(close) < 20:
            return None

        # --- 1yr return (clamped to [-1, 3] before scoring) ---
        total_return = float((close.iloc[-1] - close.iloc[0]) / close.iloc[0])
        return_score = (min(max(total_return, -1.0), 3.0) + 1.0) / 4.0 * 100.0

        # --- Max drawdown (rolling peak-to-trough) ---
        rolling_max = close.cummax()
        drawdowns = (close - rolling_max) / rolling_max
        max_dd = float(drawdowns.min())  # most negative value
        # map [-1, 0] -> [0, 100]; less drawdown = higher score
        drawdown_score = (1.0 + max(max_dd, -1.0)) * 100.0

        # --- Monthly consistency (% of months with positive return) ---
        monthly = close.resample("ME").last().pct_change().dropna()
        if len(monthly) == 0:
            consistency_score = 50.0
        else:
            pct_positive = float((monthly > 0).sum()) / len(monthly)
            consistency_score = pct_positive * 100.0

        score = (return_score + drawdown_score + consistency_score) / 3.0
        return round(min(max(score, 0.0), 100.0), 2)

    except Exception as exc:
        logger.warning("compute_long_term_score failed for %s: %s", ticker, exc)
        return None


def compute_factors_for_ticker(
    ticker: str,
    history: "pd.DataFrame",       # full multi-ticker yf.download() result (30d)
    all_histories: "pd.DataFrame",  # same object — used for relative_strength
    domain_tickers: list[str],      # all tickers in this stock's domain
) -> dict[str, float | None]:
    """Compute all 5 raw factor values for a single ticker from a 30-day history DataFrame.

    Each factor is independently wrapped in try/except so one failure does not block others.
    volatility and financial_ratio are pre-inverted (multiplied by -1.0) before returning
    so that higher raw value = better score.

    Returns
    -------
    dict with keys: momentum, volume_change, volatility, relative_strength, financial_ratio.
    Values are float or None when the factor cannot be computed.
    """
    try:
        # --- Factor 1: momentum (5-day price return) ---
        momentum: float | None = None
        try:
            close_series = history["Close"][ticker].dropna()
            if len(close_series) >= 6:
                val = float(close_series.pct_change(5).iloc[-1])
                momentum = None if math.isnan(val) else val
        except Exception as exc:
            logger.warning("momentum computation failed for %s: %s", ticker, exc)

        # --- Factor 2: volume_change (5-day % change) ---
        volume_change: float | None = None
        try:
            vol_series = history["Volume"][ticker].dropna()
            if len(vol_series) >= 6:
                val = float(vol_series.pct_change(5).iloc[-1])
                volume_change = None if math.isnan(val) else val
        except Exception as exc:
            logger.warning("volume_change computation failed for %s: %s", ticker, exc)

        # --- Factor 3: volatility (21-day rolling std — INVERTED before returning) ---
        volatility: float | None = None
        try:
            close_series = history["Close"][ticker].dropna()
            if len(close_series) >= 22:
                log_returns = np.log(close_series / close_series.shift(1)).dropna()
                vol_raw = float(log_returns.rolling(21).std(ddof=0).iloc[-1])
                if not math.isnan(vol_raw):
                    volatility = -1.0 * vol_raw  # INVERT: lower std = less risky = higher score
        except Exception as exc:
            logger.warning("volatility computation failed for %s: %s", ticker, exc)

        # --- Factor 4: relative_strength (ticker return minus median of domain peers) ---
        relative_strength: float | None = None
        try:
            stock_return_val = float(all_histories["Close"][ticker].pct_change(5).iloc[-1])
            if not math.isnan(stock_return_val):
                peer_returns = []
                for peer in domain_tickers:
                    try:
                        r = float(all_histories["Close"][peer].pct_change(5).iloc[-1])
                        if not math.isnan(r):
                            peer_returns.append(r)
                    except Exception:
                        pass
                if peer_returns:
                    median_return = float(np.median(peer_returns))
                    relative_strength = stock_return_val - median_return
        except Exception as exc:
            logger.warning("relative_strength computation failed for %s: %s", ticker, exc)

        # --- Factor 5: financial_ratio (trailingPE — INVERTED before returning) ---
        financial_ratio: float | None = None
        try:
            info = yf.Ticker(ticker).info
            pe = info.get("trailingPE")  # .get() — NEVER dict-style access
            if pe is not None:
                financial_ratio = -1.0 * float(pe)  # INVERT: lower PE = cheaper = higher score
        except Exception as exc:
            logger.warning("financial_ratio computation failed for %s: %s", ticker, exc)

        return {
            "momentum": momentum,
            "volume_change": volume_change,
            "volatility": volatility,
            "relative_strength": relative_strength,
            "financial_ratio": financial_ratio,
        }

    except Exception as exc:
        logger.warning("compute_factors_for_ticker failed entirely for %s: %s", ticker, exc)
        return {
            "momentum": None,
            "volume_change": None,
            "volatility": None,
            "relative_strength": None,
            "financial_ratio": None,
        }
