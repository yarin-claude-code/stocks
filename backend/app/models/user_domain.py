import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class UserDomain(Base):
    __tablename__ = "user_domains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    tickers: Mapped[list["UserDomainTicker"]] = relationship(
        back_populates="domain", cascade="all, delete-orphan"
    )


class UserDomainTicker(Base):
    __tablename__ = "user_domain_tickers"

    domain_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_domains.id", ondelete="CASCADE"), primary_key=True
    )
    ticker: Mapped[str] = mapped_column(String(10), primary_key=True)
    domain: Mapped["UserDomain"] = relationship(back_populates="tickers")
