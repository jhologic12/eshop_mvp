from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# --- Añadimos el path del proyecto para que Python encuentre los módulos ---
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))



# --- Importamos configuración y modelos ---
from app.core.config import settings
from app.core.database import Base
from app.models import user, product, CartItem, CartItem_item  # importa todos tus modelos
# --- Configuración base de Alembic ---
config = context.config

# Si tienes logging configurado en alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Establece la URL de la base de datos desde tu configuración
config.set_main_option("sqlalchemy.url", settings.database_url)

# Aquí se definen los metadatos de los modelos
target_metadata = Base.metadata

# --- Funciones de ejecución ---
def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones en modo 'online'."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
