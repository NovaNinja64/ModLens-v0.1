"""Enumerations shared by ModLens contracts."""

from enum import StrEnum


class StorefrontType(StrEnum):
    STEAM = "steam"
    GOG = "gog"
    EPIC = "epic"
    MICROSOFT_STORE = "microsoft_store"
    OTHER = "other"


class ModManagerType(StrEnum):
    VORTEX = "vortex"
    MO2 = "mo2"
    OTHER = "other"


class DiscoveryConfidence(StrEnum):
    CONFIRMED = "confirmed"
    PROBABLE = "probable"
    UNKNOWN = "unknown"


class DiscoveryMethod(StrEnum):
    AUTO_DETECTED = "auto_detected"
    MANUAL_SELECTION = "manual_selection"
    IMPORTED = "imported"


class DiscoveryStatus(StrEnum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    ERROR = "error"
    INCOMPLETE = "incomplete"
    CANCELLED = "cancelled"


class DiscoveryEntityType(StrEnum):
    GAME = "game"
    STOREFRONT = "storefront"
    STOREFRONT_LIBRARY = "storefront_library"
    MOD_MANAGER = "mod_manager"
    MANAGER_INSTANCE = "manager_instance"
    MOD_PROFILE = "mod_profile"


class DiscoveryEventType(StrEnum):
    STARTED = "started"
    PROGRESS = "progress"
    ENTITY_DISCOVERED = "entity_discovered"
    WARNING = "warning"
    ERROR = "error"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
