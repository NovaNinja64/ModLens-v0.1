"""Mod-manager application, instance, and profile contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from pydantic import Field

from modlens.models.base import IdentifiedModel
from modlens.models.enums import ModManagerType


class ModManagerInstallation(IdentifiedModel):
    """The installed manager application, not an individual configuration."""

    manager_type: ModManagerType
    install_path: Path
    executable_path: Path
    version: str | None = None
    install_source: str | None = None


class ManagerInstance(IdentifiedModel):
    """A configured manager instance and its filesystem locations."""

    manager_installation_id: UUID
    name: str = Field(min_length=1)
    root_path: Path
    downloads_path: Path | None = None
    mods_path: Path | None = None
    overwrite_path: Path | None = None
    game_installation_id: UUID | None = None


class ModProfile(IdentifiedModel):
    """A named configuration belonging to a manager instance."""

    manager_instance_id: UUID
    name: str = Field(min_length=1)
    game_installation_id: UUID | None = None
    enabled_mod_ids: tuple[UUID, ...] = ()
    load_order: tuple[str, ...] = ()
    ini_settings: tuple[tuple[str, str], ...] = ()
    is_active: bool = False
