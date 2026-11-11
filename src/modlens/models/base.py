"""Base types for shared ModLens contracts.

This package is intentionally independent of other internal modlens packages.
Only the Python standard library and third-party validation libraries belong here.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from modlens.models.enums import DiscoveryConfidence, DiscoveryMethod


class ContractModel(BaseModel):
    """Base class for immutable, strictly validated application contracts."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_default=True,
    )


class DiscoveryMetadata(ContractModel):
    """Provenance and confidence associated with a discovery observation."""

    method: DiscoveryMethod
    confidence: DiscoveryConfidence
    source: str = Field(min_length=1)
    evidence: tuple[str, ...] = ()
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class IdentifiedModel(ContractModel):
    """Base for entities with stable UUID identity and optional provenance."""

    id: UUID = Field(default_factory=uuid4)
    discovery: DiscoveryMetadata | None = None
