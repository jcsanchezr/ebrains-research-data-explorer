from sqlalchemy import inspect
from sqlalchemy.orm import Session

from ebrains_explorer.database.base import Base
from ebrains_explorer.database.models import (
    DatasetEntityLink,
    DatasetVersion,
    IngestSnapshot,
    KGEntity,
)
from ebrains_explorer.database.session import build_engine


def test_expected_tables_are_registered() -> None:
    expected_tables = {
        "dataset_versions",
        "kg_entities",
        "dataset_entity_links",
        "ingest_snapshots",
    }

    assert expected_tables <= set(Base.metadata.tables)


def test_models_round_trip_with_sqlite() -> None:
    engine = build_engine("sqlite+pysqlite:///:memory:")

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        dataset = DatasetVersion(
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
        )

        entity = KGEntity(
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

        dataset.entity_links.append(
            DatasetEntityLink(
                entity=entity,
                relation_type="keywords",
                position=0,
            )
        )

        snapshot = IngestSnapshot(
            source_uri="https://example.org/datasets/1",
            source="ebrains",
            schema_type="DatasetVersion",
            payload={
                "@id": "https://example.org/datasets/1",
                "@type": "DatasetVersion",
            },
        )

        session.add_all([dataset, snapshot])
        session.commit()

        assert dataset.display_name == "Example dataset"
        assert len(dataset.entity_links) == 1
        assert dataset.entity_links[0].relation_type == "keywords"
        assert dataset.entity_links[0].entity.label == "brain mapping"

    table_names = set(inspect(engine).get_table_names())

    assert {
        "dataset_versions",
        "kg_entities",
        "dataset_entity_links",
        "ingest_snapshots",
    } <= table_names

    engine.dispose()
