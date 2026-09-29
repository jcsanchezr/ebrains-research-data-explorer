from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ebrains_explorer.database.models import (
    DatasetEntityLink,
    DatasetVersion,
    IngestSnapshot,
    KGEntity,
)
from ebrains_explorer.models.normalized_dataset import (
    NormalizedDatasetVersion,
)
from ebrains_explorer.models.resolved_entity import ResolvedEntity


def get_or_create_entity(
    session: Session,
    resolved: ResolvedEntity,
) -> KGEntity:
    """Create or update a normalized KG entity."""

    entity = session.scalar(
        select(KGEntity).where(KGEntity.source_uri == resolved.source_uri)
    )

    if entity is None:
        entity = KGEntity(
            source_uri=resolved.source_uri,
            source_uuid=resolved.source_uuid,
            entity_type=resolved.entity_type,
            label=resolved.label,
            raw_payload=resolved.raw_payload,
        )
        session.add(entity)
    else:
        entity.source_uuid = resolved.source_uuid
        entity.entity_type = resolved.entity_type
        entity.label = resolved.label
        entity.raw_payload = resolved.raw_payload

    return entity


def persist_dataset_version(
    session: Session,
    normalized: NormalizedDatasetVersion,
) -> DatasetVersion:
    """Persist one normalized dataset and its provenance atomically."""

    dataset = session.scalar(
        select(DatasetVersion).where(DatasetVersion.source_uri == normalized.source_uri)
    )

    if dataset is None:
        dataset = DatasetVersion(
            source_uri=normalized.source_uri,
            source_type=normalized.source_type,
        )
        session.add(dataset)

    dataset.short_name = normalized.short_name
    dataset.full_name = normalized.full_name
    dataset.description = normalized.description
    dataset.release_date = normalized.release_date
    dataset.version_identifier = normalized.version_identifier
    dataset.version_innovation = normalized.version_innovation
    dataset.homepage = normalized.homepage
    dataset.how_to_cite = normalized.how_to_cite
    dataset.source_type = normalized.source_type

    session.flush()

    session.execute(
        delete(DatasetEntityLink).where(DatasetEntityLink.dataset_id == dataset.id)
    )

    entity_cache: dict[str, KGEntity] = {}

    for relation_type, resolved_entities in normalized.relations.items():
        for position, resolved in enumerate(resolved_entities):
            entity = entity_cache.get(resolved.source_uri)

            if entity is None:
                entity = get_or_create_entity(session, resolved)
                session.flush()
                entity_cache[resolved.source_uri] = entity

            session.add(
                DatasetEntityLink(
                    dataset_id=dataset.id,
                    entity_id=entity.id,
                    relation_type=relation_type,
                    position=position,
                )
            )

    session.add(
        IngestSnapshot(
            source_uri=normalized.source_uri,
            source="ebrains",
            schema_type=normalized.source_type,
            payload=normalized.raw_payload,
        )
    )

    session.flush()

    return dataset
