"""Typed discovery results and immutable progress events."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import Field

from modlens.models.base import ContractModel
from modlens.models.enums import (
    DiscoveryEntityType,
    DiscoveryEventType,
    DiscoveryStatus,
)
from modlens.models.installations import (
    GameInstallation,
    StorefrontInstallation,
    StorefrontLibrary,
)
from modlens.models.managers import ManagerInstance, ModManagerInstallation, ModProfile


class DiscoverySessionResult(ContractModel):
    """Final, typed aggregate produced by one discovery session."""

    session_id: UUID = Field(default_factory=uuid4)
    status: DiscoveryStatus
    started_at: datetime
    completed_at: datetime | None = None
    game_installations: tuple[GameInstallation, ...] = ()
    storefront_installations: tuple[StorefrontInstallation, ...] = ()
    storefront_libraries: tuple[StorefrontLibrary, ...] = ()
    mod_manager_installations: tuple[ModManagerInstallation, ...] = ()
    manager_instances: tuple[ManagerInstance, ...] = ()
    mod_profiles: tuple[ModProfile, ...] = ()
    errors: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


class DiscoveryProgressEvent(ContractModel):
    """Framework-neutral immutable progress notification.

    UI adapters may translate these events into Qt signals. Discovery code and
    contracts must not depend on PySide6.
    """

    event_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    event_type: DiscoveryEventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    message: str = Field(min_length=1)
    completed_count: int = Field(default=0, ge=0)
    total_count: int | None = Field(default=None, ge=0)
    entity_type: DiscoveryEntityType | None = None
    entity_id: UUID | None = None
