from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import engine, Base, seed_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (Alembic handles migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed initial domain and stock data
    await seed_db()
    yield
    await engine.dispose()


app = FastAPI(title="Smart Stock Ranker", lifespan=lifespan)


@app.get("/")
async def root():
    return {"status": "ok"}
