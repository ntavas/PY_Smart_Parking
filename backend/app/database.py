import os
from .models import Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()  # Load from .env

DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql+asyncpg://postgres_local:MyStrongPassw0rd!@localhost:5432/sm_parking"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)  # Async engine
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    # Create tables (on startup)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# For direct queries (e.g., MQTT consumer)
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        return session