from collections import defaultdict
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..database import get_db
from ..models.ranking_result import RankingResult

router = APIRouter(prefix="/api", tags=["rankings"])


class FactorBreakdown(BaseModel):
    momentum: float | None
    volume_change: float | None
    volatility: float | None
    relative_strength: float | None
    financial_ratio: float | None


class StockRanking(BaseModel):
    ticker: str
    composite_score: float
    rank: int
    factors: FactorBreakdown
    computed_at: datetime


class DomainRankings(BaseModel):
    domain: str
    top5: list[StockRanking]


class RankingsResponse(BaseModel):
    domains: list[DomainRankings]
    best_overall: StockRanking | None
    last_fetched: datetime | None


def _row_to_stock_ranking(row: RankingResult) -> StockRanking:
    return StockRanking(
        ticker=row.ticker,
        composite_score=row.composite_score,
        rank=row.rank,
        factors=FactorBreakdown(
            momentum=row.momentum,
            volume_change=row.volume_change,
            volatility=row.volatility,
            relative_strength=row.relative_strength,
            financial_ratio=row.financial_ratio,
        ),
        computed_at=row.computed_at,
    )


@router.get("/rankings", response_model=RankingsResponse)
async def get_rankings(db: AsyncSession = Depends(get_db)):
    latest_q = select(func.max(RankingResult.computed_at)).scalar_subquery()
    rows = (
        await db.execute(
            select(RankingResult)
            .where(RankingResult.computed_at == latest_q)
            .order_by(RankingResult.domain, RankingResult.rank)
        )
    ).scalars().all()

    if not rows:
        return RankingsResponse(domains=[], best_overall=None, last_fetched=None)

    last_fetched = rows[0].computed_at
    by_domain: dict[str, list[RankingResult]] = defaultdict(list)
    for row in rows:
        by_domain[row.domain].append(row)

    domains = [
        DomainRankings(
            domain=domain,
            top5=[_row_to_stock_ranking(r) for r in domain_rows[:5]],
        )
        for domain, domain_rows in sorted(by_domain.items())
    ]

    best_row = max(rows, key=lambda r: r.composite_score)
    best_overall = _row_to_stock_ranking(best_row)

    return RankingsResponse(domains=domains, best_overall=best_overall, last_fetched=last_fetched)


@router.get("/rankings/{domain}", response_model=list[StockRanking])
async def get_domain_rankings(domain: str, db: AsyncSession = Depends(get_db)):
    latest_q = select(func.max(RankingResult.computed_at)).scalar_subquery()
    rows = (
        await db.execute(
            select(RankingResult)
            .where(
                RankingResult.computed_at == latest_q,
                RankingResult.domain == domain,
            )
            .order_by(RankingResult.rank)
        )
    ).scalars().all()

    if not rows:
        raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found or no data")

    return [_row_to_stock_ranking(r) for r in rows]
