"""Mod-manager application, instance, and profile contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from pydantic import Field

from modlens.models.base import IdentifiedModel
from modlens.models.enums import ModManagerType


class ModManagerInstallation(IdentifiedModel):
    """An installed manager application, separate from its instances and profiles.

    For Mod Organizer 2 (MO2), this represents the installed application and
    executable (for example, ModOrganizer.exe). Its configured instances and
    their mod, download, and overwrite directories belong to ManagerInstance.
    For Vortex, this represents the Vortex application installation itself;
    per-user configuration and staging locations are not the application
    installation directory and must not be inferred from it.
    """

    manager_type: ModManagerType
    install_path: Path
    executable_path: Path
    version: str | None = None
    install_source: str | None = None


class ManagerInstance(IdentifiedModel):
    """A configured manager environment and the paths that define its state.

    MO2 supports multiple instances associated with one installed application.
    Each instance owns its configuration root and may have distinct mods,
    downloads, and overwrite directories; these paths must be recorded here,
    not on ModManagerInstallation. Vortex generally operates as one application
    instance with per-game profiles and staging locations. Its user-data and
    staging paths belong to this configured-environment contract rather than
    being treated as the Vortex executable's installation directory.
    """

    manager_installation_id: UUID
    name: str = Field(min_length=1)
    root_path: Path
    downloads_path: Path | None = None
    mods_path: Path | None = None
    overwrite_path: Path | None = None
    game_installation_id: UUID | None = None


class ModProfile(IdentifiedModel):
    """A named mod configuration belonging to a manager instance.

    MO2 profiles are configurations within an MO2 instance. Vortex profiles
    are game-specific configurations within its application environment.
    Enabled mods, effective load order, and profile-specific INI settings
    belong here; they must not be confused with the manager application
    installation or the instance's filesystem roots.
    """

    manager_instance_id: UUID
    name: str = Field(min_length=1)
    game_installation_id: UUID | None = None
    enabled_mod_ids: tuple[UUID, ...] = ()
    load_order: tuple[str, ...] = ()
    ini_settings: tuple[tuple[str, str], ...] = ()
    is_active: bool = False
