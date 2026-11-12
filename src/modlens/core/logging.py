
"""Logging configuration for ModLens."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOGGER_NAME = "modlens"
HANDLER_MARKER = "_modlens_handler"


def configure_logging(level: str, log_file: Path) -> logging.Logger:
    """Configure and return the dedicated ModLens logger."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.propagate = False

    normalized_level = level.upper() if isinstance(level, str) else ""
    numeric_level = logging.getLevelNamesMapping().get(normalized_level)

    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    logger.setLevel(numeric_level)

    # Remove only handlers owned by ModLens.
    for existing_handler in list(logger.handlers):
        if getattr(existing_handler, HANDLER_MARKER, False):
            logger.removeHandler(existing_handler)
            existing_handler.close()

    log_file = Path(log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        log_file,
        maxBytes=2_000_000,
        backupCount=4,
        encoding="utf-8",
    )
    setattr(handler, HANDLER_MARKER, True)

    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"
        )
    )

    logger.addHandler(handler)

    return logger


def shutdown_logging() -> None:
    """Remove and close only handlers owned by ModLens."""
    logger = logging.getLogger(LOGGER_NAME)

    for handler in list(logger.handlers):
        if getattr(handler, HANDLER_MARKER, False):
            logger.removeHandler(handler)
            handler.close()
