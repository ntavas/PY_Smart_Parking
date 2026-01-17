"""
database.py - Database and Cache Configuration

This file sets up:
- PostgreSQL async connection using SQLAlchemy
- Redis client for caching parking spot data
- Helper functions to get database sessions
"""

import os
from .models import Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import redis.asyncio as redis

load_dotenv()


# =============================================================================
# PostgreSQL Database Configuration
# =============================================================================

DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql+asyncpg://postgres_local:MyStrongPassw0rd!@localhost:5432/sm_parking"

# Async engine for non-blocking database operations
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Session factory for creating database sessions
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# =============================================================================
# Redis Cache Configuration
# =============================================================================

REDIS_HOST = os.getenv("REDIS_HOST") or "localhost"
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Redis client instance used throughout the application
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


# =============================================================================
# Database Helper Functions
# =============================================================================

async def init_db():
    """Create all database tables defined in models.py (runs on startup)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """Dependency injection helper for FastAPI routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_session() -> AsyncSession:
    """Get a standalone session for use outside of request context (e.g., MQTT consumer)."""
    async with AsyncSessionLocal() as session:
        return session
