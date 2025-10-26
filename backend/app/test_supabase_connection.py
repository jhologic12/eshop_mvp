# app/test_supabase_connection.py
from sqlalchemy import text
from app.core.config import settings
from sqlalchemy import create_engine

def main():
    print("Database URL:", settings.database_url)

    # Crear engine con la URL de Supabase
    engine = create_engine(settings.database_url)

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()
            print("✅ Conexión exitosa a la base de datos Supabase")
            print("PostgreSQL version:", version[0])
    except Exception as e:
        print("❌ Error de conexión:", e)

if __name__ == "__main__":
    main()
