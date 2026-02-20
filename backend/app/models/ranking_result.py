from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class RankingResult(Base):
    __tablename__ = "ranking_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    domain: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    composite_score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    momentum: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume_change: Mapped[float | None] = mapped_column(Float, nullable=True)
    volatility: Mapped[float | None] = mapped_column(Float, nullable=True)
    relative_strength: Mapped[float | None] = mapped_column(Float, nullable=True)
    financial_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    long_term_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
