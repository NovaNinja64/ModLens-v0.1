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
    ManagerInstance,
    ModManagerInstallation,
    ModManagerType,
    ModProfile,
    StorefrontInstallation,
    StorefrontLibrary,
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
    [
        None,
        StorefrontType.GOG,
        StorefrontType.EPIC,
        StorefrontType.MICROSOFT_STORE,
        StorefrontType.OTHER,
    ],
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
    with pytest.raises(ValidationError, match="Extra"):
        GameInstallation(
            game_id="skyrim-special-edition",
            name="Skyrim",
            install_path=Path("G:/Games/Skyrim"),
            unexpected_field=True,
        )


def test_path_json_round_trip_uses_native_pydantic_serialization():
    original_path = Path("G:/Games/Skyrim")

    game = GameInstallation(
        game_id="skyrim-special-edition",
        name="Skyrim Special Edition",
        install_path=original_path,
    )

    payload = game.model_dump(mode="json")
    assert Path(payload["install_path"]) == original_path

    restored = GameInstallation.model_validate_json(game.model_dump_json())
    assert restored.install_path == original_path


def test_uuid_json_serialization_uses_canonical_hyphenated_string():
    game = GameInstallation(
        game_id="skyrim-special-edition",
        name="Skyrim Special Edition",
        install_path=Path("G:/Games/Skyrim"),
    )

    serialized_id = game.model_dump(mode="json")["id"]
    assert serialized_id == str(game.id)
    assert len(serialized_id) == 36
    assert [len(part) for part in serialized_id.split("-")] == [8, 4, 4, 4, 12]


def test_discovery_metadata_records_provenance_and_confidence():
    metadata = DiscoveryMetadata(
        method=DiscoveryMethod.AUTO_DETECTED,
        confidence=DiscoveryConfidence.PROBABLE,
        source="Steam library manifest",
        evidence=("appmanifest_489830.acf",),
    )
    assert metadata.confidence is DiscoveryConfidence.PROBABLE
    assert metadata.discovered_at.tzinfo is not None


def test_discovery_metadata_rejects_empty_source():
    with pytest.raises(ValidationError):
        DiscoveryMetadata(
            method=DiscoveryMethod.AUTO_DETECTED,
            confidence=DiscoveryConfidence.CONFIRMED,
            source="",
        )


def test_discovery_metadata_rejects_naive_timestamp():
    with pytest.raises(ValidationError, match="timezone-aware"):
        DiscoveryMetadata(
            method=DiscoveryMethod.AUTO_DETECTED,
            confidence=DiscoveryConfidence.CONFIRMED,
            source="test",
            discovered_at=datetime(2026, 11, 11, 12, 0, 0),
        )


def test_discovery_metadata_accepts_aware_timestamp():
    timestamp = datetime(2026, 11, 11, 12, 0, 0, tzinfo=UTC)
    metadata = DiscoveryMetadata(
        method=DiscoveryMethod.AUTO_DETECTED,
        confidence=DiscoveryConfidence.CONFIRMED,
        source="test",
        discovered_at=timestamp,
    )
    assert metadata.discovered_at == timestamp


def test_game_version_validates_non_negative_components():
    version = GameVersion(major=1, minor=6, patch=1170, raw="1.6.1170")
    assert (version.major, version.minor, version.patch) == (1, 6, 1170)
    with pytest.raises(ValidationError):
        GameVersion(major=-1)


def test_storefront_installation_constructs_with_optional_defaults():
    installation = StorefrontInstallation(
        storefront_type=StorefrontType.STEAM,
        install_path=Path("G:/Steam"),
    )
    assert installation.executable_path is None
    assert installation.version is None


def test_storefront_library_requires_availability_state():
    with pytest.raises(ValidationError):
        StorefrontLibrary(
            storefront_installation_id=uuid4(),
            library_path=Path("G:/SteamLibrary"),
        )


def test_storefront_library_constructs_with_required_fields():
    library = StorefrontLibrary(
        storefront_installation_id=uuid4(),
        library_path=Path("G:/SteamLibrary"),
        is_available=True,
    )
    assert library.is_available is True
    assert library.name is None


def test_mod_manager_installation_constructs_with_optional_defaults():
    installation = ModManagerInstallation(
        manager_type=ModManagerType.MO2,
        install_path=Path("G:/ModOrganizer"),
        executable_path=Path("G:/ModOrganizer/ModOrganizer.exe"),
    )
    assert installation.version is None
    assert installation.install_source is None


def test_manager_instance_constructs_with_optional_defaults():
    instance = ManagerInstance(
        manager_installation_id=uuid4(),
        name="Default",
        root_path=Path("G:/ModOrganizer/instances/Default"),
    )
    assert instance.downloads_path is None
    assert instance.mods_path is None
    assert instance.overwrite_path is None
    assert instance.game_installation_id is None


def test_mod_profile_constructs_with_empty_configuration_defaults():
    profile = ModProfile(
        manager_instance_id=uuid4(),
        name="Default",
    )
    assert profile.enabled_mod_ids == ()
    assert profile.load_order == ()
    assert profile.ini_settings == ()
    assert profile.is_active is False


def test_discovery_session_result_uses_typed_collections():
    result = DiscoverySessionResult(
        status=DiscoveryStatus.CANCELLED,
        started_at=datetime.now(UTC),
        errors=("Scan cancelled by user",),
    )
    assert result.game_installations == ()
    assert result.status is DiscoveryStatus.CANCELLED


def test_discovery_session_result_accepts_populated_game_installations():
    game = GameInstallation(
        game_id="skyrim-special-edition",
        name="Skyrim Special Edition",
        install_path=Path("G:/Games/Skyrim"),
    )
    result = DiscoverySessionResult(
        status=DiscoveryStatus.FOUND,
        started_at=datetime.now(UTC),
        game_installations=(game,),
    )
    assert result.game_installations == (game,)
    assert isinstance(result.game_installations[0], GameInstallation)


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


def test_progress_event_rejects_naive_timestamp():
    with pytest.raises(ValidationError, match="timezone-aware"):
        DiscoveryProgressEvent(
            session_id=uuid4(),
            event_type=DiscoveryEventType.PROGRESS,
            message="Scanning",
            timestamp=datetime(2026, 11, 11, 12, 0, 0),
        )


def test_progress_event_accepts_aware_timestamp():
    timestamp = datetime(2026, 11, 11, 12, 0, 0, tzinfo=UTC)
    event = DiscoveryProgressEvent(
        session_id=uuid4(),
        event_type=DiscoveryEventType.PROGRESS,
        message="Scanning",
        timestamp=timestamp,
    )
    assert event.timestamp == timestamp


def test_exception_hierarchy_is_consistent():
    assert issubclass(ConfigurationError, ModLensError)
    assert issubclass(DatabaseError, ModLensError)
    assert issubclass(MigrationError, DatabaseError)
    assert issubclass(DiscoveryError, ModLensError)
    assert issubclass(RegistryAccessError, DiscoveryError)
    assert issubclass(PathAccessError, DiscoveryError)
    assert issubclass(ParseError, DiscoveryError)
