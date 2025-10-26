from app.db.session import engine, SessionLocal
from app.db.base_class import Base

# Dependencia para inyección de sesiones en endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inicialización de la base de datos
def init_db():
    """
    Crea todas las tablas si no existen.
    Importa los modelos dentro de la función para evitar dependencias circulares.
    """
    import app.models.user
    import app.models.product
    import app.models.cart
    import app.models.payment
    import app.models.payment_attempt

    Base.metadata.create_all(bind=engine)
