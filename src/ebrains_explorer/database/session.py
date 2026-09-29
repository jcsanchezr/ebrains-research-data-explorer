from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from ebrains_explorer.config import get_settings


def build_engine(database_url: str) -> Engine:
    """Build a SQLAlchemy engine for a database URL."""
    return create_engine(
        database_url,
        pool_pre_ping=True,
    )


@lru_cache
def get_engine() -> Engine:
    """Return the application's configured SQLAlchemy engine."""
    database_url = get_settings().database_url

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured. "
            "Set it in the environment or in a local .env file."
        )

    return build_engine(database_url)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    """Return the configured SQLAlchemy session factory."""
    return sessionmaker(
        bind=get_engine(),
        class_=Session,
        autoflush=False,
        expire_on_commit=False,
    )
