from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config.settings import settings


# SQLAlchemy 2.0 Declarative Base Class
class Base(DeclarativeBase):
    pass


# Async Database Engine Creation
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,         # এক সাথে সর্বোচ্চ খোলা রাখার কানেকশন সংখ্যা
    max_overflow=20,      # অতিরিক্ত লোড সামলানোর সর্বোচ্চ উইন্ডো
    pool_pre_ping=True,   # সেশন ডেড হয়ে গেলে অটো-রিকানেক্ট চেক
    pool_recycle=300,     # ৫০০ সেকেন্ড পর পর ড্রপ হওয়া কানেকশন রিসেট
    connect_args={
        "statement_cache_size": 0 
    }
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# FastAPI Dependency Injector
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI রিকোয়েস্টে ডাটাবেজ সেশন হ্যান্ডেল করার জন্য ডিপেন্ডেন্সি জেনারেটর।
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


