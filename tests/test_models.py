from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from modlens.core.exceptions import (
    ConfigurationError,
    DatabaseError,
    DiscoveryError,
    MigrationError,
    ModLensError,
    ParseError,
    PathAccessError,
    RegistryAccessError,
)
from modlens.models import (
    DiscoveryConfidence,
    DiscoveryEventType,
    DiscoveryMetadata,
    DiscoveryMethod,
    DiscoveryProgressEvent,
    DiscoverySessionResult,
    DiscoveryStatus,
    GameInstallation,
    GameVersion,
    StorefrontType,
)


def test_steam_game_requires_a_storefront_library():
    with pytest.raises(ValidationError, match="containing storefront library"):
        GameInstallation(
            game_id="skyrim-special-edition",
            name="Skyrim Special Edition",
            install_path=Path("G:/Steam/steamapps/common/Skyrim Special Edition"),
            storefront_type=StorefrontType.STEAM,
        )


def test_steam_game_accepts_library_reference():
    game = GameInstallation(
        game_id="skyrim-special-edition",
        name="Skyrim Special Edition",
        install_path=Path("G:/Steam/steamapps/common/Skyrim Special Edition"),
        storefront_type=StorefrontType.STEAM,
        storefront_library_id=uuid4(),
    )
    assert game.storefront_type is StorefrontType.STEAM
    assert game.storefront_library_id is not None


@pytest.mark.parametrize(
    "storefront",
    [None, StorefrontType.GOG, StorefrontType.EPIC, StorefrontType.OTHER],
)
def test_non_steam_game_does_not_require_library(storefront):
    game = GameInstallation(
        game_id="skyrim-special-edition",
        name="Skyrim Special Edition",
        install_path=Path("G:/Games/Skyrim"),
        storefront_type=storefront,
    )
    assert game.storefront_library_id is None


def test_contract_models_are_immutable():
    game = GameInstallation(
        game_id="skyrim-special-edition",
        name="Skyrim Special Edition",
        install_path=Path("G:/Games/Skyrim"),
    )
    with pytest.raises(ValidationError):
        game.name = "Changed"


def test_contract_models_reject_unknown_fields():
    with pytest.raises(ValidationError, match="extra"):
        GameInstallation(
            game_id="skyrim-special-edition",
            name="Skyrim",
            install_path=Path("G:/Games/Skyrim"),
            unexpected_field=True,
        )


def test_path_json_round_trip_uses_native_pydantic_serialization():
    game = GameInstallation(
        game_id="skyrim-special-edition",
        name="Skyrim Special Edition",
        install_path=Path("G:/Games/Skyrim"),
    )
    payload = game.model_dump(mode="json")
    assert payload["install_path"] == "G:/Games/Skyrim"
    restored = GameInstallation.model_validate(payload)
    assert restored.install_path == game.install_path


def test_discovery_metadata_records_provenance_and_confidence():
    metadata = DiscoveryMetadata(
        method=DiscoveryMethod.AUTO_DETECTED,
        confidence=DiscoveryConfidence.PROBABLE,
        source="Steam library manifest",
        evidence=("appmanifest_489830.acf",),
    )
    assert metadata.confidence is DiscoveryConfidence.PROBABLE
    assert metadata.discovered_at.tzinfo is not None


def test_game_version_validates_non_negative_components():
    version = GameVersion(major=1, minor=6, patch=1170, raw="1.6.1170")
    assert (version.major, version.minor, version.patch) == (1, 6, 1170)
    with pytest.raises(ValidationError):
        GameVersion(major=-1)


def test_discovery_session_result_uses_typed_collections():
    result = DiscoverySessionResult(
        status=DiscoveryStatus.CANCELLED,
        started_at=datetime.now(UTC),
        errors=("Scan cancelled by user",),
    )
    assert result.game_installations == ()
    assert result.status is DiscoveryStatus.CANCELLED


def test_progress_event_is_immutable_and_framework_neutral():
    event = DiscoveryProgressEvent(
        session_id=uuid4(),
        event_type=DiscoveryEventType.PROGRESS,
        message="Scanning Steam libraries",
        completed_count=1,
        total_count=3,
    )
    assert event.completed_count == 1
    with pytest.raises(ValidationError):
        event.message = "Changed"


def test_exception_hierarchy_is_consistent():
    assert issubclass(ConfigurationError, ModLensError)
    assert issubclass(DatabaseError, ModLensError)
    assert issubclass(MigrationError, DatabaseError)
    assert issubclass(DiscoveryError, ModLensError)
    assert issubclass(RegistryAccessError, DiscoveryError)
    assert issubclass(PathAccessError, DiscoveryError)
    assert issubclass(ParseError, DiscoveryError)
