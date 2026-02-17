import logging
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from .config import settings
from .services.data_fetcher import fetch_all_stocks, SEED_TICKERS
from .models.score_snapshot import ScoreSnapshot
from .models.stock import Stock

logger = logging.getLogger(__name__)

# Sync engine for the scheduler thread (yfinance + DB writes are sync)
_sync_db_url = settings.database_url.replace("sqlite+aiosqlite", "sqlite")
_sync_engine = create_engine(_sync_db_url, connect_args={"check_same_thread": False})


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


def create_scheduler() -> BackgroundScheduler:
    """Creates and configures the APScheduler instance. Caller must call .start()."""
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        fetch_cycle,
        IntervalTrigger(minutes=settings.fetch_interval_minutes),
        id="data_fetch",
        replace_existing=True,
        max_instances=1,  # Prevents overlapping runs if a fetch takes longer than the interval
    )
    return scheduler
