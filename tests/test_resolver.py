from typing import Any

from ebrains_explorer.ingestion.resolver import (
    as_list,
    entity_label,
    resolve_object,
    serialize_entity,
)


class FakeEntity:
    id = "https://example.org/entities/123"
    uuid = "123"
    name = "brain mapping"

    def to_jsonld(self) -> dict[str, Any]:
        return {
            "@id": self.id,
            "@type": "TermSuggestion",
            "name": self.name,
        }


class FakeProxy:
    def __init__(self, entity: FakeEntity) -> None:
        self.entity = entity

    def resolve(self, client: Any) -> FakeEntity:
        return self.entity


def test_as_list_none() -> None:
    assert as_list(None) == []


def test_as_list_scalar() -> None:
    assert as_list("value") == ["value"]


def test_as_list_existing_list() -> None:
    assert as_list(["a", "b"]) == ["a", "b"]


def test_entity_label() -> None:
    entity = FakeEntity()

    assert entity_label(entity) == "brain mapping"


def test_resolve_object() -> None:
    entity = FakeEntity()
    proxy = FakeProxy(entity)

    assert resolve_object(proxy, object()) is entity


def test_serialize_entity() -> None:
    entity = serialize_entity(FakeEntity())

    assert entity.source_uri == "https://example.org/entities/123"
    assert entity.source_uuid == "123"
    assert entity.entity_type == "FakeEntity"
    assert entity.label == "brain mapping"
    assert entity.raw_payload["name"] == "brain mapping"
