from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # These must exist in the environment, or the app will refuse to start
    DATABASE_URL: str
    REDIS_URL: str
    
    # This has a default fallback
    INVENTORY_PORT: str = "50052"

    # Pydantic will automatically look for a .env file
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

# We instantiate it once. Now the rest of the app can just import `settings`
settings = Settings()