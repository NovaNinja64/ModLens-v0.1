
from types import SimpleNamespace

import pytest

import modlens.app as app_module
from modlens.core.application_lifecycle import (
    ApplicationLifecycle,
    LifecycleState,
)
from modlens.core.exceptions import ApplicationStartupError


def install_fakes(monkeypatch, *, exec_error=None):
    calls = []
    lifecycle_instances = []

    def fake_shutdown_logging():
        calls.append("logging_shutdown")

    class TrackingLifecycle(ApplicationLifecycle):
        def __init__(self):
            super().__init__()
            self.shutdown_calls = 0
            lifecycle_instances.append(self)

        def shutdown(self):
            self.shutdown_calls += 1
            calls.append("shutdown")
            super().shutdown()

    class FakeSignal:
        def connect(self, callback):
            self.callback = callback

    class FakeApplication:
        def __init__(self, arguments):
            calls.append("qt")
            self.aboutToQuit = FakeSignal()

        def setApplicationName(self, name):
            pass

        def setOrganizationName(self, name):
            pass

        def exec(self):
            calls.append("exec")

            if exec_error is not None:
                raise exec_error

            self.aboutToQuit.callback()
            return 0
        
        def quit(self):
            calls.append("quit")
            self.aboutToQuit.callback()

    class FakeWindow:
        def __init__(self):
            calls.append("window")

        def show(self):
            calls.append("show")

        def close(self):
            calls.append("close")

    config = SimpleNamespace(
        log_level="INFO",
        log_file="modlens.log",
        database_file="modlens.sqlite3",
    )

    def load_config():
        calls.append("configuration")
        return config

    def configure_logging(level, log_file):
        calls.append("logging")

    def initialize_database(database_file):
        calls.append("database")

    monkeypatch.setattr(
        app_module, "ApplicationLifecycle", TrackingLifecycle
    )
    monkeypatch.setattr(app_module, "QApplication", FakeApplication)
    monkeypatch.setattr(app_module, "MainWindow", FakeWindow)
    monkeypatch.setattr(app_module, "load_config", load_config)
    monkeypatch.setattr(app_module, "configure_logging", configure_logging)
    monkeypatch.setattr(
        app_module, "initialize_database", initialize_database
    )
    monkeypatch.setattr(
        app_module, "shutdown_logging", fake_shutdown_logging
    )

    return calls, lifecycle_instances


def test_application_starts_and_shuts_down_in_order(monkeypatch):
    calls, lifecycle_instances = install_fakes(monkeypatch)

    result = app_module.main()

    assert result == 0
    assert calls == [
        "configuration",
        "logging",
        "database",
        "qt",
        "window",
        "show",
        "exec",
        "shutdown",
        "close",
        "quit",
        "logging_shutdown",
    ]
    assert lifecycle_instances[0].state is LifecycleState.STOPPED
    assert lifecycle_instances[0].shutdown_calls == 1


def test_startup_failure_prevents_qt_initialization(monkeypatch):
    calls, lifecycle_instances = install_fakes(monkeypatch)

    def fail_logging(level, log_file):
        raise RuntimeError("Logging initialization failed.")

    monkeypatch.setattr(
        app_module, "configure_logging", fail_logging
    )

    with pytest.raises(ApplicationStartupError):
        app_module.main()

    assert "qt" not in calls
    assert lifecycle_instances[0].state is LifecycleState.FAILED
    assert lifecycle_instances[0].shutdown_calls == 0
    assert calls[-1] == "logging_shutdown"


def test_event_loop_failure_still_triggers_shutdown(monkeypatch):
    calls, lifecycle_instances = install_fakes(
        monkeypatch,
        exec_error=RuntimeError("Qt event loop failed."),
    )

    with pytest.raises(RuntimeError, match="Qt event loop failed"):
        app_module.main()

    assert calls[-5:] == [
        "exec",
        "shutdown",
        "close",
        "quit",
        "logging_shutdown",
    ]
    assert lifecycle_instances[0].state is LifecycleState.STOPPED
    assert lifecycle_instances[0].shutdown_calls == 1


def test_reentrant_about_to_quit_does_not_shutdown_twice(monkeypatch):
    calls, lifecycle_instances = install_fakes(monkeypatch)

    result = app_module.main()

    assert result == 0
    assert lifecycle_instances[0].state is LifecycleState.STOPPED
    assert lifecycle_instances[0].shutdown_calls == 1
    assert calls.count("shutdown") == 1
    assert calls.count("close") == 1
    assert calls.count("quit") == 1
    assert calls.count("logging_shutdown") == 1
