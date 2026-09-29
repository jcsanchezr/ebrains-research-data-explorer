from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

# Import models so that they are registered in Base.metadata.
import ebrains_explorer.database.models  # noqa: F401
from alembic import context
from ebrains_explorer.config import get_settings
from ebrains_explorer.database.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


settings = get_settings()

if not settings.database_url:
    raise RuntimeError(
        "DATABASE_URL is not configured. "
        "Set it in the environment or in a local .env file."
    )

config.set_main_option(
    "sqlalchemy.url",
    settings.database_url.replace("%", "%%"),
)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without creating an Engine."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using a live database connection."""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
