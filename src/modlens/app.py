
"""ModLens application entry point."""

from __future__ import annotations

import logging
import sys
from collections.abc import Callable

from PySide6.QtWidgets import QApplication

from modlens.core.application_lifecycle import (
    ApplicationLifecycle,
    LifecycleState,
)
from modlens.core.config import AppConfig, load_config
from modlens.core.exceptions import ApplicationShutdownError
from modlens.core.logging import configure_logging, shutdown_logging
from modlens.storage.database import initialize_database
from modlens.ui.main_window import MainWindow


def main() -> int:
    lifecycle = ApplicationLifecycle()

    config: AppConfig | None = None
    app: QApplication | None = None
    window: MainWindow | None = None
    logger = logging.getLogger(__name__)

    def initialize_configuration() -> None:
        nonlocal config
        config = load_config()

    def initialize_logging() -> None:
        assert config is not None
        configure_logging(config.log_level, config.log_file)

    def initialize_database_service() -> None:
        assert config is not None
        initialize_database(config.database_file)

    def initialize_qt_application() -> Callable[[], None]:
        nonlocal app
        app = QApplication(sys.argv)
        app.setApplicationName("ModLens")
        app.setOrganizationName("ModLens")
        return app.quit

    def initialize_main_window() -> Callable[[], None]:
        nonlocal window
        window = MainWindow()
        window.show()
        return window.close

    def shutdown_application() -> None:
        if lifecycle.state in {
            LifecycleState.STOPPING,
            LifecycleState.STOPPED,
        }:
            return

        try:
            lifecycle.shutdown()
        except ApplicationShutdownError:
            logger.exception("Application shutdown encountered errors.")

    lifecycle.add_step("Configuration", initialize_configuration)
    lifecycle.add_step("Logging", initialize_logging)
    lifecycle.add_step("Database", initialize_database_service)
    lifecycle.add_step("Qt Application", initialize_qt_application)
    lifecycle.add_step("Main Window", initialize_main_window)

    try:
        lifecycle.start()

        if app is None:
            raise RuntimeError("Qt application was not initialized.")

        app.aboutToQuit.connect(shutdown_application)

        return app.exec()

    except Exception:
        logger.exception("Application execution failed.")
        raise

    finally:
        if lifecycle.state is LifecycleState.RUNNING:
            shutdown_application()

        shutdown_logging()
