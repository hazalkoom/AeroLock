from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    INVENTORY_SERVICE_URL: str = "localhost:50052"
    SEARCH_SERVICE_URL: str = "localhost:50051"
    GATEWAY_PORT: int = 8000

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

settings = Settings()