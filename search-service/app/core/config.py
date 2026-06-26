from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # This service runs on 50051 (Inventory runs on 50052)
    GRPC_PORT: int = 50051
    
    # Database and Cache Connections
    DATABASE_URL: str = "postgresql+asyncpg://aerolock_user:password123@localhost:5432/aerolock"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Cache TTL (Time To Live) in seconds - How long we keep search results in memory
    CACHE_TTL: int = 60 

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

settings = Settings()