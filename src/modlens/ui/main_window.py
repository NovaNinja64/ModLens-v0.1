from PySide6.QtWidgets import QLabel, QMainWindow, QListWidget, QStackedWidget, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ModLens")
        self.resize(1100, 720)

        root = QWidget()
        layout = QVBoxLayout(root)
        self.navigation = QListWidget()
        self.navigation.addItems([
            "Dashboard", "Games & Installations", "Mod Setup & Managers",
            "Mod Scanner", "AI Troubleshooter", "Live Assist",
            "Diagnostic Reports", "Profiles & Backups", "Module Manager", "Settings",
        ])

        self.pages = QStackedWidget()
        welcome = QWidget()
        welcome_layout = QVBoxLayout(welcome)
        heading = QLabel("Welcome to ModLens")
        heading.setStyleSheet("font-size: 24px; font-weight: 600;")
        description = QLabel(
            "Your local-first modding diagnostics workspace. "
            "Game discovery is the next implementation milestone."
        )
        description.setWordWrap(True)
        welcome_layout.addWidget(heading)
        welcome_layout.addWidget(description)
        welcome_layout.addStretch()
        self.pages.addWidget(welcome)

        self.navigation.currentRowChanged.connect(self._select_page)
        self.navigation.setCurrentRow(0)
        layout.addWidget(self.navigation)
        layout.addWidget(self.pages, 1)
        self.setCentralWidget(root)

    def _select_page(self, index: int) -> None:
        # Unimplemented destinations deliberately remain on the honest landing page.
        self.pages.setCurrentIndex(0)
