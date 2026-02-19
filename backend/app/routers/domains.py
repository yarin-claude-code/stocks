from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models.stock import Domain

router = APIRouter(prefix="/api", tags=["domains"])


@router.get("/domains")
async def list_domains(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Domain.name).order_by(Domain.name))
    return {"domains": result.scalars().all()}
