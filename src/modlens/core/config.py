from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


def app_data_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    path = Path(base) / "ModLens" if base else Path.home() / ".local" / "share" / "ModLens"
    path.mkdir(parents=True, exist_ok=True)
    return path


@dataclass(frozen=True)
class AppConfig:
    log_level: str
    log_file: Path
    database_file: Path


def load_config() -> AppConfig:
    data_dir = app_data_dir()
    config_path = data_dir / "config.json"
    values: dict = {}
    if config_path.exists():
        try:
            loaded = json.loads(config_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                values = loaded
        except (OSError, json.JSONDecodeError):
            values = {}

    log_level = str(values.get("log_level", "INFO")).upper()
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        log_level = "INFO"

    return AppConfig(
        log_level=log_level,
        log_file=data_dir / "logs" / "modlens.log",
        database_file=data_dir / "modlens.sqlite3",
    )
