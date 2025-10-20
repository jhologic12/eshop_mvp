# backend/app/core/database.py
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import uuid
from sqlalchemy.orm import declared_attr

# --- Configurar el motor de base de datos ---
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# --- Sesión de base de datos ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Clase base para los modelos ---
Base = declarative_base()


# --- Mixin para IDs tipo UUID ---
class UUIDMixin:
    @declared_attr
    def uuid(cls):
        return Column(
            String(36),
            primary_key=True,
            default=lambda: str(uuid.uuid4()),
            unique=True,
            index=True,
            nullable=False,
        )


# --- Dependencia para inyección en los endpoints ---
def get_db():
    """
    Devuelve una sesión de base de datos y la cierra automáticamente
    al finalizar la solicitud.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Inicialización de la base de datos ---
def init_db():
    """
    Crea todas las tablas si no existen.
    Importa los modelos dentro de la función para evitar dependencias circulares.
    """
    import app.models.user
    import app.models.cart
    import app.models.product
    import app.models.payment

    Base.metadata.create_all(bind=engine)
