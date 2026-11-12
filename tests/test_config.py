
"""Tests for application configuration."""

import json

import pytest

from modlens.core.config import app_data_dir, load_config
from modlens.core.exceptions import PathAccessError


def test_load_config_uses_safe_defaults(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    config = load_config()

    assert config.log_level == "INFO"
    assert config.database_file.name == "modlens.sqlite3"
    assert config.log_file.name == "modlens.log"


def test_missing_config_file_uses_defaults(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    config = load_config()

    assert config.log_level == "INFO"


def test_malformed_json_uses_defaults(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    data_dir = app_data_dir()
    (data_dir / "config.json").write_text("{invalid", encoding="utf-8")

    config = load_config()

    assert config.log_level == "INFO"


@pytest.mark.parametrize("contents", ["[]", "null", '"text"', "123", "true"])
def test_non_object_json_uses_defaults(monkeypatch, tmp_path, contents):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    data_dir = app_data_dir()
    (data_dir / "config.json").write_text(contents, encoding="utf-8")

    config = load_config()

    assert config.log_level == "INFO"


@pytest.mark.parametrize("level", ["debug", "INFO", "warning", "ERROR", "CRITICAL"])
def test_valid_log_levels_are_normalized(monkeypatch, tmp_path, level):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    data_dir = app_data_dir()
    (data_dir / "config.json").write_text(
        json.dumps({"log_level": level}), encoding="utf-8"
    )

    config = load_config()

    assert config.log_level == level.upper()


@pytest.mark.parametrize("level", ["INVALID", "", None, 123, [], {}])
def test_invalid_log_levels_fall_back_to_info(monkeypatch, tmp_path, level):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    data_dir = app_data_dir()
    (data_dir / "config.json").write_text(
        json.dumps({"log_level": level}), encoding="utf-8"
    )

    config = load_config()

    assert config.log_level == "INFO"


def test_relative_localappdata_is_rejected(monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", "relative/path")

    with pytest.raises(PathAccessError):
        app_data_dir()


def test_data_directory_creation_failure_is_translated(
    monkeypatch, tmp_path
):
    invalid_base = tmp_path / "not_a_directory"
    invalid_base.write_text("file", encoding="utf-8")
    monkeypatch.setenv("LOCALAPPDATA", str(invalid_base))

    with pytest.raises(PathAccessError):
        app_data_dir()


def test_configuration_paths_remain_inside_data_directory(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    config = load_config()

    assert config.log_file == tmp_path / "ModLens" / "logs" / "modlens.log"
    assert config.database_file == tmp_path / "ModLens" / "modlens.sqlite3"
