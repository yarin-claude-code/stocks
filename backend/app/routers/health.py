from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.score_snapshot import ScoreSnapshot

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Returns system health and last successful data fetch timestamp."""
    # Query the most recent ScoreSnapshot fetched_at across all tickers
    result = await db.execute(select(func.max(ScoreSnapshot.fetched_at)))
    last_fetched = result.scalar_one_or_none()

    return {
        "status": "ok",
        "last_fetched": last_fetched.isoformat() if last_fetched else None,
        "data_available": last_fetched is not None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
