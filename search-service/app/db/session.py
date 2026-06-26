from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

# Create the async engine pointing to our Postgres database
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# Create the session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False, 
    autoflush=False
)