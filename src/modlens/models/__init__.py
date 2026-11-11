"""Shared, immutable data contracts used across ModLens."""

from modlens.models.base import ContractModel, DiscoveryMetadata
from modlens.models.discovery import DiscoveryProgressEvent, DiscoverySessionResult
from modlens.models.enums import (
    DiscoveryConfidence,
    DiscoveryEntityType,
    DiscoveryEventType,
    DiscoveryMethod,
    DiscoveryStatus,
    ModManagerType,
    StorefrontType,
)
from modlens.models.installations import (
    GameInstallation,
    GameVersion,
    StorefrontInstallation,
    StorefrontLibrary,
)
from modlens.models.managers import ManagerInstance, ModManagerInstallation, ModProfile

__all__ = [
    "ContractModel",
    "DiscoveryConfidence",
    "DiscoveryEntityType",
    "DiscoveryEventType",
    "DiscoveryMetadata",
    "DiscoveryMethod",
    "DiscoveryProgressEvent",
    "DiscoverySessionResult",
    "DiscoveryStatus",
    "GameInstallation",
    "GameVersion",
    "ManagerInstance",
    "ModManagerInstallation",
    "ModManagerType",
    "ModProfile",
    "StorefrontInstallation",
    "StorefrontLibrary",
    "StorefrontType",
]
