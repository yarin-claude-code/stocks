from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers.auth import router as auth_router
from .routers.custom_domains import router as custom_domains_router
from .routers.domains import router as domains_router
from .routers.health import router as health_router
from .routers.history import router as history_router
from .routers.preferences import router as preferences_router
from .routers.rankings import router as rankings_router
from .scheduler import create_scheduler
from .seed import seed_db

_scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler
    # Initialize DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed initial data
    await seed_db()
    # Start background scheduler
    _scheduler = create_scheduler()
    _scheduler.start()
    yield
    # Graceful shutdown
    if _scheduler:
        _scheduler.shutdown(wait=False)
    await engine.dispose()


app = FastAPI(title="Smart Stock Ranker", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "PUT", "POST", "DELETE"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(rankings_router)
app.include_router(domains_router)
app.include_router(preferences_router)
app.include_router(auth_router)
app.include_router(custom_domains_router)
app.include_router(history_router, prefix="/api")


@app.get("/")
async def root():
    return {"status": "ok"}
