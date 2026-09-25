from typing import Any

from pydantic import BaseModel


class ResolvedEntity(BaseModel):
    """Source-neutral representation of a resolved KG entity."""

    source_uri: str
    source_uuid: str | None = None
    entity_type: str
    label: str | None = None
    raw_payload: dict[str, Any]
