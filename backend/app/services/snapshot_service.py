import logging
from datetime import date, timedelta

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.daily_snapshot import DailySnapshot
from app.models.ranking_result import RankingResult
from app.models.stock import Domain

logger = logging.getLogger(__name__)


def compute_trend(scores: list[float]) -> float:
    """Linear slope over scores list. Returns 0.0 if fewer than 2 points."""
    if len(scores) < 2:
        return 0.0
    x = np.arange(len(scores), dtype=float)
    slope, _ = np.polyfit(x, scores, 1)
    return float(slope)


def snapshot_job() -> None:
    """
    EOD job: reads latest RankingResult per ticker, writes/updates DailySnapshot for today.
    Uses sync engine (_sync_engine) — runs in APScheduler BackgroundScheduler thread.
    """
    from app.scheduler import _sync_engine  # avoid circular import at module level

    today = date.today()
    with Session(_sync_engine) as session:
        # Build domain_name -> domain_id map
        domain_map: dict[str, int] = {
            name: id_
            for name, id_ in session.execute(select(Domain.name, Domain.id)).all()
        }

        # Get latest RankingResult per ticker (max computed_at subquery)
        from sqlalchemy import func
        latest_subq = (
            select(RankingResult.ticker, func.max(RankingResult.computed_at).label("max_computed_at"))
            .group_by(RankingResult.ticker)
            .subquery()
        )
        results = session.execute(
            select(RankingResult).join(
                latest_subq,
                (RankingResult.ticker == latest_subq.c.ticker)
                & (RankingResult.computed_at == latest_subq.c.max_computed_at),
            )
        ).scalars().all()

        if not results:
            logger.warning("snapshot_job: no RankingResult rows found, skipping")
            return

        for result in results:
            # Get last 7 DailySnapshot scores for this ticker (excluding today)
            past = session.execute(
                select(DailySnapshot.composite_score)
                .where(
                    DailySnapshot.ticker == result.ticker,
                    DailySnapshot.snap_date >= today - timedelta(days=7),
                    DailySnapshot.snap_date < today,
                )
                .order_by(DailySnapshot.snap_date)
            ).scalars().all()

            slope = compute_trend(list(past) + [result.composite_score])
            domain_id = domain_map.get(result.domain)

            snap = session.merge(DailySnapshot(
                ticker=result.ticker,
                snap_date=today,
                composite_score=result.composite_score,
                rank=result.rank,
                domain_id=domain_id,
                trend_slope=slope,
            ))

        session.commit()
        logger.info("snapshot_job: wrote %d snapshots for %s", len(results), today)
