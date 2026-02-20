from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.models.user_preference import UserPreference
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/preferences", tags=["preferences"])


class PreferencesOut(BaseModel):
    domains: list[str]


class PreferencesIn(BaseModel):
    domains: list[str]


@router.get("", response_model=PreferencesOut)
async def get_preferences(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == uuid.UUID(user_id))
    )
    pref = result.scalar_one_or_none()
    return PreferencesOut(domains=pref.domains if pref else [])


@router.put("", response_model=PreferencesOut)
async def put_preferences(
    body: PreferencesIn,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uid = uuid.UUID(user_id)
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == uid)
    )
    pref = result.scalar_one_or_none()
    if pref is None:
        pref = UserPreference(user_id=uid, domains=body.domains)
        db.add(pref)
    else:
        pref.domains = body.domains
    await db.commit()
    return PreferencesOut(domains=pref.domains)
