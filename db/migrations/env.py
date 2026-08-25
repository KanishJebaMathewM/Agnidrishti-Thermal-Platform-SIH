import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Ensure backend folder is in path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

# Import target metadata
from app.models.base import Base
# Import models to register them on Base.metadata
import app.models.observation
import app.models.thermal_source
import app.models.event
import app.models.authority
import app.models.notification
import app.models.geography
import app.models.ml

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url():
    # Load settings from app config
    from app.config import settings
    url = os.getenv("DATABASE_URL", settings.database_url)
    # Ensure sync driver is used for migrations (replace async driver if specified)
    if "postgresql+psycopg://" in url:
        return url
    elif "postgresql+asyncpg://" in url:
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
    elif "postgresql://" in url:
        # standard postgresql:// maps to psycopg
        return url.replace("postgresql://", "postgresql+psycopg://")
    return url

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            include_object=None
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
