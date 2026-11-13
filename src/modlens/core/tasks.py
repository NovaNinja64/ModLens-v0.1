"""Background task execution utilities."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from modlens.core.cancellation import CancellationToken
from modlens.core.exceptions import TaskCancelledError


class TaskSignals(QObject):
    started = Signal()
    finished = Signal()
    failed = Signal(str)
    cancelled = Signal()
    result = Signal(object)


class FunctionTask(QRunnable):
    """Run a callable away from the UI thread and emit its outcome.

    Cancellation-aware callables can opt in to receiving the task's
    CancellationToken as a keyword argument named ``cancellation_token``.
    """

    def __init__(
        self,
        function: Callable[..., Any],
        *args: Any,
        cancellation_token: CancellationToken | None = None,
        pass_cancellation_token: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.cancellation_token = cancellation_token or CancellationToken()
        self.pass_cancellation_token = pass_cancellation_token
        self.signals = TaskSignals()

    @Slot()
    def run(self) -> None:
        self.signals.started.emit()

        try:
            self.cancellation_token.raise_if_cancelled()

            if self.pass_cancellation_token:
                result = self.function(
                    *self.args,
                    cancellation_token=self.cancellation_token,
                    **self.kwargs,
                )
            else:
                result = self.function(*self.args, **self.kwargs)

            self.signals.result.emit(result)

        except TaskCancelledError:
            self.signals.cancelled.emit()

        except Exception as exc:  # noqa: BLE001
            self.signals.failed.emit(f"{type(exc).__name__}: {exc}")

        finally:
            self.signals.finished.emit()
