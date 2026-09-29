from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from fairgraph import KGClient
from sqlalchemy.orm import Session, sessionmaker

from ebrains_explorer.database.repository import persist_dataset_version
from ebrains_explorer.ingestion.normalizer import normalize_dataset_version


@dataclass(slots=True)
class IngestionFailure:
    """One dataset that could not be ingested."""

    source_uri: str | None
    error_type: str
    message: str


@dataclass(slots=True)
class BatchIngestionResult:
    """Summary of one batch ingestion run."""

    attempted: int = 0
    succeeded: int = 0
    failed: int = 0
    dataset_ids: list[int] = field(default_factory=list)
    failures: list[IngestionFailure] = field(default_factory=list)


def ingest_dataset_batch(
    datasets: Iterable[Any],
    client: KGClient,
    session_factory: sessionmaker[Session],
) -> BatchIngestionResult:
    """Normalize and persist datasets using one transaction per dataset."""

    result = BatchIngestionResult()

    for source_dataset in datasets:
        result.attempted += 1

        source_id = getattr(source_dataset, "id", None)
        source_uri = str(source_id) if source_id is not None else None

        try:
            normalized = normalize_dataset_version(
                source_dataset,
                client,
            )

            with session_factory.begin() as session:
                dataset = persist_dataset_version(
                    session,
                    normalized,
                )
                dataset_id = dataset.id

            result.succeeded += 1
            result.dataset_ids.append(dataset_id)

        except Exception as exc:
            result.failed += 1
            result.failures.append(
                IngestionFailure(
                    source_uri=source_uri,
                    error_type=type(exc).__name__,
                    message=str(exc),
                )
            )

    return result
