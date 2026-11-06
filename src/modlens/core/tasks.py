from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class TaskSignals(QObject):
    started = Signal()
    finished = Signal()
    failed = Signal(str)
    result = Signal(object)


class FunctionTask(QRunnable):
    """Run a callable away from the UI thread and emit its outcome."""

    def __init__(self, function, *args, **kwargs) -> None:
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = TaskSignals()

    @Slot()
    def run(self) -> None:
        self.signals.started.emit()
        try:
            self.signals.result.emit(self.function(*self.args, **self.kwargs))
        except Exception as exc:
            self.signals.failed.emit(f"{type(exc).__name__}: {exc}")
        finally:
            self.signals.finished.emit()
