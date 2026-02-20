import logging
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import yfinance as yf

from sqlalchemy.orm import selectinload
from .config import settings
from .services.data_fetcher import fetch_all_stocks, compute_factors_for_ticker, SEED_TICKERS
from .services.ranking_engine import rank_domain
from .models.score_snapshot import ScoreSnapshot
from .models.stock import Stock, Domain
from .models.ranking_result import RankingResult

logger = logging.getLogger(__name__)

# Sync engine for the scheduler thread (yfinance + DB writes are sync)
_sync_engine = create_engine(settings.sync_database_url)


def fetch_cycle() -> None:
    """Called by APScheduler every N minutes. Fetches data and persists to DB.
    On yfinance failure, returns without modifying DB — last-known-good data is retained."""
    logger.info("fetch_cycle: starting data fetch")
    data = fetch_all_stocks(SEED_TICKERS)
    if not data:
        logger.warning("fetch_cycle: no data returned, skipping DB write (last-known-good retained)")
        return

    now = datetime.now(timezone.utc)
    with Session(_sync_engine) as session:
        for ticker, values in data.items():
            snapshot = ScoreSnapshot(
                ticker=ticker,
                close_price=values["close_price"],
                volume=values["volume"],
                fetched_at=now,
            )
            session.add(snapshot)
            # Update last_updated on the Stock row
            stock = session.execute(select(Stock).where(Stock.ticker == ticker)).scalar_one_or_none()
            if stock:
                stock.last_updated = now
        session.commit()
    logger.info("fetch_cycle: persisted %d tickers at %s", len(data), now.isoformat())

    # --- Factor computation and ranking ---
    # Load domain groupings from DB
    with Session(_sync_engine) as session:
        domain_rows = session.execute(
            select(Domain).options(selectinload(Domain.stocks))
        ).scalars().all()
        domain_groups = {d.name: [s.ticker for s in d.stocks] for d in domain_rows}

    if not domain_groups:
        logger.warning("fetch_cycle: no domains found in DB, skipping ranking")
        return

    # Download 30d history for factor computation (single batch call)
    try:
        all_tickers = [t for group in domain_groups.values() for t in group]
        history = yf.download(
            all_tickers,
            period="30d",
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=True,
        )
    except Exception as exc:
        logger.error("Factor history download failed: %s", exc)
        return

    now_computed = datetime.now(timezone.utc)
    ranking_count = 0
    with Session(_sync_engine) as session:
        for domain_name, tickers in domain_groups.items():
            stocks_data: dict[str, dict] = {}
            for ticker in tickers:
                factors = compute_factors_for_ticker(
                    ticker=ticker,
                    history=history,
                    all_histories=history,
                    domain_tickers=tickers,
                )
                stocks_data[ticker] = factors

            results = rank_domain(stocks_data)
            for ticker, score in results.items():
                logger.info(
                    "Domain=%s ticker=%s score=%.1f rank=%d",
                    domain_name, ticker, score.composite_score, score.rank,
                )
                fs = score.factor_scores
                session.add(RankingResult(
                    ticker=ticker,
                    domain=domain_name,
                    composite_score=score.composite_score,
                    rank=score.rank,
                    momentum=fs["momentum"].raw if "momentum" in fs else None,
                    volume_change=fs["volume_change"].raw if "volume_change" in fs else None,
                    volatility=fs["volatility"].raw if "volatility" in fs else None,
                    relative_strength=fs["relative_strength"].raw if "relative_strength" in fs else None,
                    financial_ratio=fs["financial_ratio"].raw if "financial_ratio" in fs else None,
                    computed_at=now_computed,
                ))
                ranking_count += 1
        session.commit()
    logger.info("fetch_cycle: persisted %d ranking results", ranking_count)


def create_scheduler() -> BackgroundScheduler:
    """Creates and configures the APScheduler instance. Caller must call .start()."""
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        fetch_cycle,
        IntervalTrigger(minutes=settings.fetch_interval_minutes),
        id="data_fetch",
        replace_existing=True,
        max_instances=1,  # Prevents overlapping runs if a fetch takes longer than the interval
        next_run_time=datetime.now(timezone.utc),  # Fire immediately on startup
    )
    return scheduler
