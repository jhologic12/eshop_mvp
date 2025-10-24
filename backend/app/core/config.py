
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os

class Settings(BaseSettings):
    environment: str = "development"
    app_name: str = "Eshop MVP API"
    app_version: str = "1.0.0"
    debug: bool = True
    database_url: str = "sqlite:///./app.db"
    backend_cors_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# función cacheada (evita recarga innecesaria)
@lru_cache()
def get_settings() -> Settings:
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        env_file = ".env.prod"
    elif env == "test":
        env_file = ".env.test"
    else:
        env_file = ".env"

    return Settings(_env_file=env_file)

settings = Settings()

# URL base del servicio de mock de pagos
MOCK_PAYMENT_URL = os.getenv("MOCK_PAYMENT_URL", "http://127.0.0.1:8001")