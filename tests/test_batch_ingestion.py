from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from ebrains_explorer.database.base import Base
from ebrains_explorer.database.models import (
    DatasetVersion,
    IngestSnapshot,
)
from ebrains_explorer.database.session import build_engine
from ebrains_explorer.services.ingestion import ingest_dataset_batch


class FakeDataset:
    def __init__(
        self,
        source_uri: str | None,
        short_name: str,
    ) -> None:
        self.id = source_uri
        self.short_name = short_name
        self.full_name = None
        self.description = None
        self.release_date = None
        self.version_identifier = "v1"
        self.version_innovation = None
        self.homepage = None
        self.how_to_cite = None

    def to_jsonld(self) -> dict[str, Any]:
        return {
            "@id": self.id,
            "@type": "DatasetVersion",
            "shortName": self.short_name,
        }


def test_batch_continues_after_dataset_failure() -> None:
    engine = build_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    session_factory = sessionmaker(
        bind=engine,
        class_=Session,
        expire_on_commit=False,
    )

    datasets = [
        FakeDataset(
            "https://example.org/datasets/1",
            "Valid dataset",
        ),
        FakeDataset(
            None,
            "Invalid dataset",
        ),
    ]

    result = ingest_dataset_batch(
        datasets,
        object(),  # type: ignore[arg-type]
        session_factory,
    )

    assert result.attempted == 2
    assert result.succeeded == 1
    assert result.failed == 1
    assert len(result.dataset_ids) == 1
    assert len(result.failures) == 1
    assert result.failures[0].error_type == "ValueError"

    with session_factory() as session:
        dataset_count = session.scalar(select(func.count()).select_from(DatasetVersion))
        snapshot_count = session.scalar(
            select(func.count()).select_from(IngestSnapshot)
        )

        assert dataset_count == 1
        assert snapshot_count == 1

    engine.dispose()
