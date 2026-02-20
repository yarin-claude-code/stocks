import asyncio
import uuid

import yfinance as yf
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user_domain import UserDomain, UserDomainTicker
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/domains/custom", tags=["custom_domains"])


class DomainOut(BaseModel):
    id: int
    name: str
    tickers: list[str]

    class Config:
        from_attributes = True


class DomainCreateIn(BaseModel):
    name: str
    tickers: list[str]


class DomainUpdateIn(BaseModel):
    tickers: list[str]


def _validate_ticker_sync(symbol: str) -> bool:
    try:
        info = yf.Ticker(symbol.upper()).info
        return bool(info.get("shortName") or info.get("longName"))
    except Exception:
        return False


async def validate_ticker(symbol: str) -> bool:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _validate_ticker_sync, symbol)


async def _check_tickers(tickers: list[str]) -> None:
    results = await asyncio.gather(*[validate_ticker(t) for t in tickers])
    invalid = [t for t, ok in zip(tickers, results) if not ok]
    if invalid:
        raise HTTPException(status_code=422, detail=f"Invalid tickers: {', '.join(invalid)}")


@router.get("", response_model=list[DomainOut])
async def get_custom_domains(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserDomain)
        .where(UserDomain.user_id == uuid.UUID(user_id))
        .options(selectinload(UserDomain.tickers))
    )
    domains = result.scalars().all()
    return [
        DomainOut(id=d.id, name=d.name, tickers=[t.ticker for t in d.tickers])
        for d in domains
    ]


@router.post("", response_model=DomainOut, status_code=201)
async def create_custom_domain(
    body: DomainCreateIn,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _check_tickers(body.tickers)
    domain = UserDomain(user_id=uuid.UUID(user_id), name=body.name)
    db.add(domain)
    await db.flush()
    for ticker in body.tickers:
        db.add(UserDomainTicker(domain_id=domain.id, ticker=ticker.upper()))
    await db.commit()
    await db.refresh(domain)
    result = await db.execute(
        select(UserDomain)
        .where(UserDomain.id == domain.id)
        .options(selectinload(UserDomain.tickers))
    )
    domain = result.scalar_one()
    return DomainOut(id=domain.id, name=domain.name, tickers=[t.ticker for t in domain.tickers])


@router.put("/{domain_id}", response_model=DomainOut)
async def update_custom_domain(
    domain_id: int,
    body: DomainUpdateIn,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserDomain)
        .where(UserDomain.id == domain_id, UserDomain.user_id == uuid.UUID(user_id))
        .options(selectinload(UserDomain.tickers))
    )
    domain = result.scalar_one_or_none()
    if domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    await _check_tickers(body.tickers)
    for t in list(domain.tickers):
        await db.delete(t)
    await db.flush()
    for ticker in body.tickers:
        db.add(UserDomainTicker(domain_id=domain.id, ticker=ticker.upper()))
    await db.commit()
    result = await db.execute(
        select(UserDomain)
        .where(UserDomain.id == domain.id)
        .options(selectinload(UserDomain.tickers))
    )
    domain = result.scalar_one()
    return DomainOut(id=domain.id, name=domain.name, tickers=[t.ticker for t in domain.tickers])


@router.delete("/{domain_id}", status_code=204)
async def delete_custom_domain(
    domain_id: int,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserDomain).where(
            UserDomain.id == domain_id, UserDomain.user_id == uuid.UUID(user_id)
        )
    )
    domain = result.scalar_one_or_none()
    if domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    await db.delete(domain)
    await db.commit()
