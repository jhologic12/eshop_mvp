# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Entorno y app
    environment: str = "development"
    app_name: str = "Eshop MVP API"
    app_version: str = "1.0.0"
    debug: bool = True
    backend_cors_origins: str = "*"

    # URL de conexión a Supabase PostgreSQL
    database_url: str

    # Configuración Cloudinary
    cloudinary_cloud_name: str | None = None
    cloudinary_api_key: str | None = None
    cloudinary_api_secret: str | None = None

    # URL del servicio de mock de pagos
    mock_payment_url: str = "https://mock-payment-kmts.onrender.com"

    # Permite variables extra en el .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

@lru_cache()
def get_settings() -> Settings:
    env = os.getenv("ENVIRONMENT", "development")
    env_file = {
        "production": ".env.prod",
        "test": ".env.test"
    }.get(env, ".env")
    return Settings(_env_file=env_file)

# Instancia global
settings = get_settings()
