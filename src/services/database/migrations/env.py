import asyncio
from logging.config import fileConfig
from typing import no_type_check

import nest_asyncio
from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.settings import get_settings
from src.services.database.models.base import Base

target_metadata = Base.metadata
config = context.config
fileConfig(config.config_file_name)
application_settings = get_settings()
config.set_main_option(
    "sqlalchemy.url",
    str(
        URL.create(
            drivername="postgresql+asyncpg",
            username=application_settings.database.USER,
            password=application_settings.database.PASS,
            database=application_settings.database.NAME,
            host=application_settings.database.HOST,
        )
    ),
)


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_server_default=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


@no_type_check
def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_server_default=True,
        compare_type=True,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",  # noqa
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(run_migrations_online())
