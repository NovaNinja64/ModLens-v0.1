
"""Integration tests for the ModLens foundation components."""

import json
import logging
import sqlite3

from modlens.core.config import load_config
from modlens.core.logging import configure_logging, shutdown_logging
from modlens.storage.database import initialize_database


def test_configuration_logging_and_database_work_together(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    data_dir = tmp_path / "ModLens"
    data_dir.mkdir()

    (data_dir / "config.json").write_text(
        json.dumps({"log_level": "DEBUG"}),
        encoding="utf-8",
    )

    config = load_config()

    assert config.log_level == "DEBUG"
    assert config.log_file == data_dir / "logs" / "modlens.log"
    assert config.database_file == data_dir / "modlens.sqlite3"

    logger = configure_logging(config.log_level, config.log_file)

    try:
        test_logger = logging.getLogger("modlens.integration_test")
        test_logger.debug("Foundation integration test message.")

        initialize_database(config.database_file)

        assert config.log_file.exists()
        assert config.database_file.exists()

        log_contents = config.log_file.read_text(encoding="utf-8")
        assert "Foundation integration test message." in log_contents

        with sqlite3.connect(config.database_file) as connection:
            version = connection.execute(
                "SELECT version FROM schema_migrations"
            ).fetchone()

        assert version == (1,)
        assert logger.level == logging.DEBUG

    finally:
        shutdown_logging()
