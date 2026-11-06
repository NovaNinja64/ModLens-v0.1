from __future__ import annotations

import sys
from PySide6.QtWidgets import QApplication

from modlens.core.config import load_config
from modlens.core.logging import configure_logging
from modlens.storage.database import initialize_database
from modlens.ui.main_window import MainWindow


def main() -> int:
    config = load_config()
    configure_logging(config.log_level, config.log_file)
    initialize_database(config.database_file)

    app = QApplication(sys.argv)
    app.setApplicationName("ModLens")
    app.setOrganizationName("ModLens")
    window = MainWindow()
    window.show()
    return app.exec()
