import logging
from sqlalchemy import select
from .database import async_session_maker
from .models.stock import Stock, Domain

logger = logging.getLogger(__name__)

SEED_DATA = {
    "AI/Tech": [
        ("AAPL", "Apple Inc."),
        ("MSFT", "Microsoft Corp."),
        ("NVDA", "NVIDIA Corp."),
        ("AMD", "Advanced Micro Devices"),
        ("GOOGL", "Alphabet Inc."),
    ],
    "EV": [
        ("TSLA", "Tesla Inc."),
        ("RIVN", "Rivian Automotive"),
    ],
    "Finance": [
        ("JPM", "JPMorgan Chase"),
        ("GS", "Goldman Sachs"),
    ],
}


async def seed_db():
    async with async_session_maker() as session:
        for domain_name, stocks in SEED_DATA.items():
            result = await session.execute(select(Domain).where(Domain.name == domain_name))
            domain = result.scalar_one_or_none()
            if not domain:
                domain = Domain(name=domain_name)
                session.add(domain)
                await session.flush()
            for ticker, name in stocks:
                result = await session.execute(select(Stock).where(Stock.ticker == ticker))
                stock = result.scalar_one_or_none()
                if not stock:
                    session.add(Stock(ticker=ticker, name=name, domain_id=domain.id))
        await session.commit()
    logger.info("seed_db: seed complete")
