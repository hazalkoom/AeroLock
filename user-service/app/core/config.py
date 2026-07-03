import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://aerolock_user:password123@localhost:5432/aerolock"
    )

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    @property
    def private_key(self) -> str:
        with open(os.path.join(self.BASE_DIR, "certs", "private_key.pem"), "r") as f:
            return f.read()

settings = Settings()