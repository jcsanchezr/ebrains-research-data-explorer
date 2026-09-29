from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ebrains_explorer.database.base import Base
from ebrains_explorer.database.models import (
    DatasetEntityLink,
    DatasetVersion,
    IngestSnapshot,
    KGEntity,
)
from ebrains_explorer.database.repository import persist_dataset_version
from ebrains_explorer.database.session import build_engine
from ebrains_explorer.models.normalized_dataset import (
    NormalizedDatasetVersion,
)
from ebrains_explorer.models.resolved_entity import ResolvedEntity


def make_dataset() -> NormalizedDatasetVersion:
    entity = ResolvedEntity(
        source_uri="https://example.org/entities/1",
        source_uuid="entity-1",
        entity_type="TermSuggestion",
        label="brain mapping",
        raw_payload={
            "@id": "https://example.org/entities/1",
            "@type": "TermSuggestion",
            "name": "brain mapping",
        },
    )

    return NormalizedDatasetVersion(
        source_uri="https://example.org/datasets/1",
        short_name="Example dataset",
        full_name=None,
        description=None,
        release_date=None,
        version_identifier="v1",
        version_innovation=None,
        homepage=None,
        how_to_cite=None,
        source_type="DatasetVersion",
        relations={"keywords": [entity]},
        raw_payload={
            "@id": "https://example.org/datasets/1",
            "@type": "DatasetVersion",
        },
    )


def test_persist_dataset_is_idempotent() -> None:
    engine = build_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    normalized = make_dataset()

    with Session(engine) as session:
        persist_dataset_version(session, normalized)
        session.commit()

        persist_dataset_version(session, normalized)
        session.commit()

        dataset_count = session.scalar(select(func.count()).select_from(DatasetVersion))

        entity_count = session.scalar(select(func.count()).select_from(KGEntity))

        link_count = session.scalar(select(func.count()).select_from(DatasetEntityLink))

        snapshot_count = session.scalar(
            select(func.count()).select_from(IngestSnapshot)
        )

        assert dataset_count == 1
        assert entity_count == 1
        assert link_count == 1
        assert snapshot_count == 2

    engine.dispose()
