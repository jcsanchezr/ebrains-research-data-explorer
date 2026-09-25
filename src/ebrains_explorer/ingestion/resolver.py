from typing import Any

from fairgraph import KGClient

from ebrains_explorer.models.resolved_entity import ResolvedEntity


def as_list(value: Any) -> list[Any]:
    """Normalize None, one object, or a list of objects to a list."""

    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def resolve_object(value: Any, client: KGClient) -> Any:
    """Resolve a fairgraph KGProxy when necessary."""

    resolver = getattr(value, "resolve", None)

    if callable(resolver):
        return resolver(client)

    return value


def entity_label(entity: Any) -> str | None:
    """Extract a useful human-readable label from an openMINDS entity."""

    for attribute in (
        "name",
        "full_name",
        "short_name",
        "preferred_ontology_identifier",
        "lookup_label",
    ):
        value = getattr(entity, attribute, None)

        if isinstance(value, str) and value.strip():
            return value.strip()

    given_name = getattr(entity, "given_name", None)
    family_name = getattr(entity, "family_name", None)

    parts = [
        part.strip()
        for part in (given_name, family_name)
        if isinstance(part, str) and part.strip()
    ]

    if parts:
        return " ".join(parts)

    return None


def serialize_entity(entity: Any) -> ResolvedEntity:
    """Convert an openMINDS object to our source-neutral representation."""

    entity_id = getattr(entity, "id", None)
    entity_uuid = getattr(entity, "uuid", None)

    payload = entity.to_jsonld()

    return ResolvedEntity(
        source_uri=str(entity_id),
        source_uuid=str(entity_uuid) if entity_uuid else None,
        entity_type=type(entity).__name__,
        label=entity_label(entity),
        raw_payload=payload,
    )


def resolve_relation(
    value: Any,
    client: KGClient,
) -> list[ResolvedEntity]:
    """Resolve every entity linked through one KG relation."""

    entities: list[ResolvedEntity] = []

    for item in as_list(value):
        resolved = resolve_object(item, client)

        if resolved is not None:
            entities.append(serialize_entity(resolved))

    return entities
