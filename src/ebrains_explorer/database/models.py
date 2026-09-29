from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from ebrains_explorer.database.base import Base

JSON_TYPE = JSON().with_variant(JSONB, "postgresql")


class DatasetVersion(Base):
    """Normalized searchable projection of a source dataset version."""

    __tablename__ = "dataset_versions"

    __table_args__ = (
        UniqueConstraint(
            "source_uri",
            name="uq_dataset_versions_source_uri",
        ),
        Index(
            "ix_dataset_versions_release_date",
            "release_date",
        ),
        Index(
            "ix_dataset_versions_source_type",
            "source_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    source_uri: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    short_name: Mapped[str | None] = mapped_column(Text)
    full_name: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)

    release_date: Mapped[date | None] = mapped_column(Date)

    version_identifier: Mapped[str | None] = mapped_column(String(128))

    version_innovation: Mapped[str | None] = mapped_column(Text)
    homepage: Mapped[str | None] = mapped_column(Text)
    how_to_cite: Mapped[str | None] = mapped_column(Text)

    source_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    entity_links: Mapped[list[DatasetEntityLink]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def display_name(self) -> str:
        """Return the best available human-readable dataset name."""
        return self.full_name or self.short_name or self.source_uri


class KGEntity(Base):
    """Source-neutral representation of a resolved graph entity."""

    __tablename__ = "kg_entities"

    __table_args__ = (
        UniqueConstraint(
            "source_uri",
            name="uq_kg_entities_source_uri",
        ),
        Index(
            "ix_kg_entities_source_uuid",
            "source_uuid",
        ),
        Index(
            "ix_kg_entities_entity_type",
            "entity_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    source_uri: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    source_uuid: Mapped[str | None] = mapped_column(String(128))

    entity_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    label: Mapped[str | None] = mapped_column(Text)

    raw_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON_TYPE,
        nullable=False,
    )

    dataset_links: Mapped[list[DatasetEntityLink]] = relationship(
        back_populates="entity",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class DatasetEntityLink(Base):
    """Typed relationship between a dataset and a resolved KG entity."""

    __tablename__ = "dataset_entity_links"

    __table_args__ = (
        Index(
            "ix_dataset_entity_links_relation_type",
            "relation_type",
        ),
    )

    dataset_id: Mapped[int] = mapped_column(
        ForeignKey(
            "dataset_versions.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    entity_id: Mapped[int] = mapped_column(
        ForeignKey(
            "kg_entities.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    relation_type: Mapped[str] = mapped_column(
        String(128),
        primary_key=True,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        default=0,
    )

    dataset: Mapped[DatasetVersion] = relationship(back_populates="entity_links")

    entity: Mapped[KGEntity] = relationship(back_populates="dataset_links")


class IngestSnapshot(Base):
    """Raw source document retained for provenance and reprocessing."""

    __tablename__ = "ingest_snapshots"

    __table_args__ = (
        Index(
            "ix_ingest_snapshots_source_uri_fetched_at",
            "source_uri",
            "fetched_at",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    source_uri: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    source: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    schema_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    payload: Mapped[dict[str, Any]] = mapped_column(
        JSON_TYPE,
        nullable=False,
    )
