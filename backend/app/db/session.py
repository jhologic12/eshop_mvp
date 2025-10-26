from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Usa la URL de PostgreSQL desde config
SQLALCHEMY_DATABASE_URL = settings.database_url

# Crea el motor de conexión
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
    # No necesitamos connect_args para PostgreSQL
)

# Crea la sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
