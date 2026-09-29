from sqlalchemy import func, select

from ebrains_explorer.database.models import (
    DatasetEntityLink,
    DatasetVersion,
    IngestSnapshot,
    KGEntity,
)
from ebrains_explorer.database.repository import persist_dataset_version
from ebrains_explorer.database.session import get_session_factory
from ebrains_explorer.ingestion.ebrains import (
    create_client,
    fetch_dataset_versions,
)
from ebrains_explorer.ingestion.normalizer import (
    normalize_dataset_version,
)


def main() -> None:
    client = create_client()
    source_dataset = fetch_dataset_versions(client, limit=1)[0]

    normalized = normalize_dataset_version(
        source_dataset,
        client,
    )

    session_factory = get_session_factory()

    with session_factory.begin() as session:
        dataset = persist_dataset_version(
            session,
            normalized,
        )

        dataset_id = dataset.id

    with session_factory() as session:
        dataset_count = session.scalar(select(func.count()).select_from(DatasetVersion))
        entity_count = session.scalar(select(func.count()).select_from(KGEntity))
        link_count = session.scalar(select(func.count()).select_from(DatasetEntityLink))
        snapshot_count = session.scalar(
            select(func.count()).select_from(IngestSnapshot)
        )

    print(f"Persisted dataset ID: {dataset_id}")
    print(f"Dataset: {normalized.short_name}")
    print()
    print(f"dataset_versions:     {dataset_count}")
    print(f"kg_entities:          {entity_count}")
    print(f"dataset_entity_links: {link_count}")
    print(f"ingest_snapshots:     {snapshot_count}")


if __name__ == "__main__":
    main()
