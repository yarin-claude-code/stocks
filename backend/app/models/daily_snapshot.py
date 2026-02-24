from datetime import date
from typing import Optional

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class DailySnapshot(Base):
    __tablename__ = "daily_snapshots"
    ticker: Mapped[str] = mapped_column(String(10), primary_key=True)
    snap_date: Mapped[date] = mapped_column(Date, primary_key=True)
    composite_score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    domain_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("domains.id"), nullable=True)
    trend_slope: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.0")
