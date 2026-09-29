import json
from typing import Any

from fairgraph import KGClient
from fairgraph.openminds.core import DatasetVersion as EbrainsDatasetVersion

from ebrains_explorer.ingestion.resolver import resolve_relation
from ebrains_explorer.models.normalized_dataset import (
    NormalizedDatasetVersion,
)

RELATION_FIELDS = (
    "license",
    "repository",
    "keywords",
    "data_types",
    "study_targets",
    "techniques",
)


def clean_text(value: Any) -> str | None:
    """Normalize an optional scalar value to clean text."""
    if value is None:
        return None

    text = str(value).strip()
    return text or None


def json_safe(payload: dict[str, Any]) -> dict[str, Any]:
    """Convert a JSON-LD payload to JSON-serializable primitives."""
    return json.loads(json.dumps(payload, default=str))


def normalize_dataset_version(
    dataset: EbrainsDatasetVersion,
    client: KGClient,
) -> NormalizedDatasetVersion:
    """Normalize one EBRAINS DatasetVersion."""

    source_uri = clean_text(getattr(dataset, "id", None))

    if source_uri is None:
        raise ValueError("DatasetVersion has no source URI")

    relations = {
        relation_name: resolve_relation(
            getattr(dataset, relation_name, None),
            client,
        )
        for relation_name in RELATION_FIELDS
    }

    return NormalizedDatasetVersion(
        source_uri=source_uri,
        short_name=clean_text(getattr(dataset, "short_name", None)),
        full_name=clean_text(getattr(dataset, "full_name", None)),
        description=clean_text(getattr(dataset, "description", None)),
        release_date=getattr(dataset, "release_date", None),
        version_identifier=clean_text(getattr(dataset, "version_identifier", None)),
        version_innovation=clean_text(getattr(dataset, "version_innovation", None)),
        homepage=clean_text(getattr(dataset, "homepage", None)),
        how_to_cite=clean_text(getattr(dataset, "how_to_cite", None)),
        source_type=type(dataset).__name__,
        relations=relations,
        raw_payload=json_safe(dataset.to_jsonld()),
    )
