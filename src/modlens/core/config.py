
"""Application configuration and data-directory management."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from modlens.core.exceptions import PathAccessError

VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def app_data_dir() -> Path:
    """Return the ModLens data directory, creating it when necessary."""
    base = os.environ.get("LOCALAPPDATA")

    try:
        if base:
            base_path = Path(base).expanduser()
            if not base_path.is_absolute():
                raise PathAccessError(
                    "LOCALAPPDATA must be an absolute path."
                )
        else:
            base_path = Path.home() / ".local" / "share"

        path = base_path / "ModLens"
        path.mkdir(parents=True, exist_ok=True)

        if not path.is_dir():
            raise PathAccessError(
                f"Application data path is not a directory: {path}"
            )

        return path

    except (OSError, RuntimeError) as exc:
        raise PathAccessError(
            "Unable to create or access the ModLens application data directory."
        ) from exc


@dataclass(frozen=True)
class AppConfig:
    log_level: str
    log_file: Path
    database_file: Path


def load_config() -> AppConfig:
    """Load configuration, falling back safely when its file is invalid."""
    data_dir = app_data_dir()
    config_path = data_dir / "config.json"
    values: dict[str, object] = {}

    if config_path.exists():
        try:
            loaded = json.loads(config_path.read_text(encoding="utf-8"))

            if isinstance(loaded, dict):
                values = loaded

        except (OSError, UnicodeError, json.JSONDecodeError):
            values = {}

    raw_level = values.get("log_level", "INFO")

    if isinstance(raw_level, str):
        log_level = raw_level.upper()
    else:
        log_level = "INFO"

    if log_level not in VALID_LOG_LEVELS:
        log_level = "INFO"

    return AppConfig(
        log_level=log_level,
        log_file=data_dir / "logs" / "modlens.log",
        database_file=data_dir / "modlens.sqlite3",
    )
