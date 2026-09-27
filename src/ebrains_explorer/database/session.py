from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ebrains_explorer.config import get_settings


def build_engine(database_url: str | None = None) -> Engine:
    """Create a SQLAlchemy engine for the configured database."""

    url = database_url or get_settings().database_url

    if not url:
        raise RuntimeError(
            "DATABASE_URL is not configured. "
            "Set it in the environment or in a local .env file."
        )

    return create_engine(
        url,
        pool_pre_ping=True,
    )


engine = build_engine()

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)
