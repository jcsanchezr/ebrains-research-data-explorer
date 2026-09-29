from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from ebrains_explorer.models.resolved_entity import ResolvedEntity


class NormalizedDatasetVersion(BaseModel):
    """Source-neutral representation of a normalized dataset version."""

    source_uri: str
    short_name: str | None = None
    full_name: str | None = None
    description: str | None = None
    release_date: date | None = None
    version_identifier: str | None = None
    version_innovation: str | None = None
    homepage: str | None = None
    how_to_cite: str | None = None
    source_type: str

    relations: dict[str, list[ResolvedEntity]] = Field(default_factory=dict)

    raw_payload: dict[str, Any]
