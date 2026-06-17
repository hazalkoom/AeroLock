import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://aerolock_user:password123@localhost:5432/aerolock"
)

engine = create_async_engine(DATABASE_URL, echo=False)

Async_session_local = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    async with Async_session_local as session:
        try:
            yield session
        finally:
            await session.close()
