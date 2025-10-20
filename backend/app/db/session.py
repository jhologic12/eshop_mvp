# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configura la URL de conexión — SQLite por defecto
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# Crea el motor de conexión
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necesario para SQLite
)

# Crea la sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
