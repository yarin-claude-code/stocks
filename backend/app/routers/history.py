from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from app.models.daily_snapshot import DailySnapshot
from app.database import get_db
from datetime import date, timedelta

router = APIRouter()


@router.get("/history/{ticker}")
async def get_history(
    ticker: str,
    days: int = Query(default=30, ge=1, le=365),
    db=Depends(get_db),
):
    since = date.today() - timedelta(days=days)
    result = await db.execute(
        select(DailySnapshot)
        .where(DailySnapshot.ticker == ticker.upper())
        .where(DailySnapshot.snap_date >= since)
        .order_by(DailySnapshot.snap_date)
    )
    rows = result.scalars().all()
    return [
        {
            "snap_date": r.snap_date.isoformat(),
            "composite_score": r.composite_score,
            "rank": r.rank,
            "trend_slope": r.trend_slope,
        }
        for r in rows
    ]
