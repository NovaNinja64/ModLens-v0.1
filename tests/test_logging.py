
"""Tests for ModLens logging configuration."""

import logging
from logging.handlers import RotatingFileHandler

import pytest

from modlens.core.logging import configure_logging


@pytest.fixture
def modlens_logger():
    logger = logging.getLogger("modlens")
    original_level = logger.level
    original_propagate = logger.propagate
    original_handlers = list(logger.handlers)

    for handler in list(logger.handlers):
        if getattr(handler, "_modlens_handler", False):
            logger.removeHandler(handler)
            handler.close()

    yield logger

    for handler in list(logger.handlers):
        if handler not in original_handlers:
            logger.removeHandler(handler)
            handler.close()

    logger.setLevel(original_level)
    logger.propagate = original_propagate


def test_configure_logging_uses_dedicated_logger(
    modlens_logger, tmp_path
):
    log_file = tmp_path / "logs" / "modlens.log"

    logger = configure_logging("INFO", log_file)

    assert logger is modlens_logger
    assert logger.name == "modlens"
    assert logger.propagate is False


def test_configure_logging_adds_rotating_file_handler(
    modlens_logger, tmp_path
):
    log_file = tmp_path / "modlens.log"

    configure_logging("INFO", log_file)

    handlers = [
        handler
        for handler in modlens_logger.handlers
        if getattr(handler, "_modlens_handler", False)
    ]

    assert len(handlers) == 1
    assert isinstance(handlers[0], RotatingFileHandler)
    assert handlers[0].baseFilename.endswith("modlens.log")


def test_repeated_configuration_does_not_duplicate_handlers(
    modlens_logger, tmp_path
):
    log_file = tmp_path / "modlens.log"

    configure_logging("INFO", log_file)
    configure_logging("INFO", log_file)

    handlers = [
        handler
        for handler in modlens_logger.handlers
        if getattr(handler, "_modlens_handler", False)
    ]

    assert len(handlers) == 1


def test_reconfiguration_replaces_owned_handler(
    modlens_logger, tmp_path
):
    first_log = tmp_path / "first.log"
    second_log = tmp_path / "second.log"

    configure_logging("INFO", first_log)
    first_handler = next(
        handler
        for handler in modlens_logger.handlers
        if getattr(handler, "_modlens_handler", False)
    )

    configure_logging("DEBUG", second_log)

    handlers = [
        handler
        for handler in modlens_logger.handlers
        if getattr(handler, "_modlens_handler", False)
    ]

    assert len(handlers) == 1
    assert handlers[0].baseFilename.endswith("second.log")
    assert first_handler not in modlens_logger.handlers
    assert first_handler.stream is None
    assert modlens_logger.level == logging.DEBUG


def test_configuration_does_not_modify_root_logger(
    modlens_logger, tmp_path
):
    root = logging.getLogger()
    original_level = root.level
    original_handlers = list(root.handlers)

    configure_logging("DEBUG", tmp_path / "modlens.log")

    assert root.level == original_level
    assert root.handlers == original_handlers


def test_configuration_does_not_remove_third_party_handlers(
    modlens_logger, tmp_path
):
    third_party_handler = logging.NullHandler()
    modlens_logger.addHandler(third_party_handler)

    configure_logging("INFO", tmp_path / "modlens.log")

    assert third_party_handler in modlens_logger.handlers


def test_configuration_falls_back_to_info_for_invalid_level(
    modlens_logger, tmp_path
):
    configure_logging("INVALID", tmp_path / "modlens.log")

    assert modlens_logger.level == logging.INFO


def test_logging_creates_parent_directories(
    modlens_logger, tmp_path
):
    log_file = tmp_path / "nested" / "logs" / "modlens.log"

    configure_logging("INFO", log_file)

    assert log_file.parent.is_dir()
