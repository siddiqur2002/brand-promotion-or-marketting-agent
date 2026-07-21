from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import router as campaign_router
from app.config.settings import settings
from app.database.session import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    অ্যাপ্লিকেশন লাইফসাইকেল ম্যানেজার:
    স্টার্টআপের সময় ডাটাবেজ টেবিল স্কিমা তৈরি করবে।
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # শাটডাউনের সময় ইঞ্জিন ক্লিনআপ
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Production-grade AI Marketing Agent using FastAPI, CrewAI, Celery, and Upstash Redis.",
    lifespan=lifespan,
)

# CORS Config (Production Security Standard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # প্রোডাকশনে নির্দিষ্ট Frontend Domain বসাবে
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# রুট যুক্ত করা
app.include_router(campaign_router)


@app.get("/health", tags=["Health Check"])
async def health_check() -> dict:
    """
    সার্ভার রানিং আছে কি না চেক করার হেলথচেক রুট।
    """
    return {"status": "healthy", "project": settings.PROJECT_NAME}


