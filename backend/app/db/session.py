from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.database_url

# 🔹 Engine con pool limitado para no superar el límite de Supabase
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,        # máximo de conexiones simultáneas permitido en free-tier
    max_overflow=0,     # no permite conexiones extra temporales
    pool_timeout=30,    # espera hasta 30s antes de fallar
    pool_pre_ping=True  # verifica la conexión antes de usarla
)

# 🔹 Sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
