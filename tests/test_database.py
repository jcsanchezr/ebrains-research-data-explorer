from sqlalchemy import text

from ebrains_explorer.database.session import build_engine


def test_build_engine() -> None:
    engine = build_engine("sqlite+pysqlite:///:memory:")

    with engine.connect() as connection:
        result = connection.scalar(text("SELECT 1"))

    assert result == 1

    engine.dispose()
