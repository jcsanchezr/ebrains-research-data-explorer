import argparse

from sqlalchemy import func, select

from ebrains_explorer.database.models import (
    DatasetEntityLink,
    DatasetVersion,
    IngestSnapshot,
    KGEntity,
)
from ebrains_explorer.database.session import get_session_factory
from ebrains_explorer.ingestion.ebrains import (
    create_client,
    fetch_dataset_versions,
)
from ebrains_explorer.services.ingestion import ingest_dataset_batch


def positive_integer(value: str) -> int:
    number = int(value)

    if number < 1:
        raise argparse.ArgumentTypeError("limit must be greater than zero")

    return number


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest released EBRAINS dataset versions."
    )

    parser.add_argument(
        "--limit",
        type=positive_integer,
        default=5,
        help="Maximum number of dataset versions to retrieve.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    client = create_client()
    datasets = fetch_dataset_versions(
        client,
        limit=args.limit,
    )

    session_factory = get_session_factory()

    result = ingest_dataset_batch(
        datasets,
        client,
        session_factory,
    )

    with session_factory() as session:
        dataset_count = session.scalar(select(func.count()).select_from(DatasetVersion))
        entity_count = session.scalar(select(func.count()).select_from(KGEntity))
        link_count = session.scalar(select(func.count()).select_from(DatasetEntityLink))
        snapshot_count = session.scalar(
            select(func.count()).select_from(IngestSnapshot)
        )

    print()
    print("BATCH")
    print(f"attempted: {result.attempted}")
    print(f"succeeded: {result.succeeded}")
    print(f"failed:    {result.failed}")

    print()
    print("DATABASE")
    print(f"dataset_versions:     {dataset_count}")
    print(f"kg_entities:          {entity_count}")
    print(f"dataset_entity_links: {link_count}")
    print(f"ingest_snapshots:     {snapshot_count}")

    if result.failures:
        print()
        print("FAILURES")

        for failure in result.failures:
            print(
                f"{failure.source_uri or '<unknown>'}: "
                f"{failure.error_type}: "
                f"{failure.message}"
            )

    return 1 if result.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
