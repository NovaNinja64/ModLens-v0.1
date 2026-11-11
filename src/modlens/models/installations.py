"""Game, storefront, and storefront-library contracts."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import UUID

from pydantic import Field, model_validator

from modlens.models.base import IdentifiedModel
from modlens.models.enums import StorefrontType


class GameVersion(IdentifiedModel):
    """Structured game version while retaining its original display value."""

    major: int = Field(ge=0)
    minor: int = Field(default=0, ge=0)
    patch: int = Field(default=0, ge=0)
    build: int | None = Field(default=None, ge=0)
    raw: str | None = None


class StorefrontInstallation(IdentifiedModel):
    """An installed storefront client, independent of its game libraries."""

    storefront_type: StorefrontType
    install_path: Path
    executable_path: Path | None = None
    version: str | None = None


class StorefrontLibrary(IdentifiedModel):
    """A library location managed by a storefront installation."""

    storefront_installation_id: UUID
    library_path: Path
    name: str | None = None
    is_available: bool
    last_checked_at: datetime | None = None


class GameInstallation(IdentifiedModel):
    """A specific installed copy of a game.

    Storefront association is optional so GOG, standalone, and manually selected
    installations remain first-class. Steam installations must identify a
    containing Steam library.
    """

    game_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    install_path: Path
    executable_path: Path | None = None
    version: GameVersion | None = None
    storefront_type: StorefrontType | None = None
    storefront_installation_id: UUID | None = None
    storefront_library_id: UUID | None = None

    @model_validator(mode="after")
    def require_library_for_steam(self) -> GameInstallation:
        if (
            self.storefront_type == StorefrontType.STEAM
            and self.storefront_library_id is None
        ):
            raise ValueError(
                "Steam game installations must reference their containing storefront library."
            )
        return self
