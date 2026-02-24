import logging

from sqlalchemy import select

from .database import async_session_maker
from .models.stock import Domain, Stock

logger = logging.getLogger(__name__)

SEED_DATA = {
    "AI/Tech":          [("AAPL","Apple Inc."),("MSFT","Microsoft Corp."),("NVDA","NVIDIA Corp."),("AMD","Advanced Micro Devices"),("GOOGL","Alphabet Inc.")],
    "EV":               [("TSLA","Tesla Inc."),("RIVN","Rivian Automotive"),("NIO","NIO Inc."),("LCID","Lucid Group")],
    "Finance":          [("JPM","JPMorgan Chase"),("GS","Goldman Sachs"),("BAC","Bank of America"),("MS","Morgan Stanley")],
    "Healthcare":       [("JNJ","Johnson & Johnson"),("UNH","UnitedHealth Group"),("PFE","Pfizer Inc."),("ABBV","AbbVie Inc.")],
    "Energy":           [("XOM","Exxon Mobil"),("CVX","Chevron Corp."),("COP","ConocoPhillips"),("SLB","SLB (Schlumberger)")],
    "Consumer":         [("AMZN","Amazon.com Inc."),("WMT","Walmart Inc."),("HD","Home Depot"),("MCD","McDonald's Corp.")],
    "Semiconductors":   [("TSM","Taiwan Semiconductor"),("INTC","Intel Corp."),("QCOM","Qualcomm Inc."),("AVGO","Broadcom Inc.")],
    "Defense":          [("LMT","Lockheed Martin"),("RTX","RTX Corp."),("NOC","Northrop Grumman"),("GD","General Dynamics")],
    "Crypto/Fintech":   [("COIN","Coinbase Global"),("PYPL","PayPal Holdings"),("V","Visa Inc."),("HOOD","Robinhood Markets")],
    "Industrials":      [("CAT","Caterpillar Inc."),("DE","Deere & Company"),("HON","Honeywell Intl."),("UPS","United Parcel Service")],
    "Media/Streaming":  [("NFLX","Netflix Inc."),("DIS","Walt Disney Co."),("SPOT","Spotify Technology"),("WBD","Warner Bros. Discovery")],
    "Real Estate":      [("AMT","American Tower"),("PLD","Prologis Inc."),("EQIX","Equinix Inc."),("SPG","Simon Property Group")],
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
