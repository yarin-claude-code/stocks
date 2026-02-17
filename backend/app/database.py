from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event, select
from .config import settings

engine = create_async_engine(settings.database_url, echo=False)


# Enable WAL mode for SQLite (better concurrent read performance)
@event.listens_for(engine.sync_engine, "connect")
def set_wal_mode(dbapi_conn, connection_record):
    dbapi_conn.execute("PRAGMA journal_mode=WAL")


async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


async def seed_db():
    """Insert seed domains and stocks if they don't already exist."""
    from .models.stock import Domain, Stock

    domain_data = [
        {"name": "AI/Tech", "stocks": [
            ("AAPL", "Apple Inc."),
            ("MSFT", "Microsoft Corp."),
            ("NVDA", "NVIDIA Corp."),
            ("AMD", "Advanced Micro Devices"),
            ("GOOGL", "Alphabet Inc."),
        ]},
        {"name": "EV", "stocks": [
            ("TSLA", "Tesla Inc."),
            ("RIVN", "Rivian Automotive"),
        ]},
        {"name": "Finance", "stocks": [
            ("JPM", "JPMorgan Chase"),
            ("GS", "Goldman Sachs"),
        ]},
    ]

    async with async_session_maker() as session:
        for domain_info in domain_data:
            result = await session.execute(
                select(Domain).where(Domain.name == domain_info["name"])
            )
            domain = result.scalar_one_or_none()
            if domain is None:
                domain = Domain(name=domain_info["name"])
                session.add(domain)
                await session.flush()

            for ticker, name in domain_info["stocks"]:
                result = await session.execute(
                    select(Stock).where(Stock.ticker == ticker)
                )
                stock = result.scalar_one_or_none()
                if stock is None:
                    stock = Stock(ticker=ticker, name=name, domain_id=domain.id)
                    session.add(stock)

        await session.commit()
