"""Cooperative task cancellation primitives."""

from __future__ import annotations

from threading import Event

from modlens.core.exceptions import TaskCancelledError


class CancellationToken:
    """Thread-safe, one-way cancellation signal for long-running tasks."""

    def __init__(self) -> None:
        self._event = Event()

    def cancel(self) -> None:
        """Request cancellation of the associated task."""
        self._event.set()

    @property
    def is_cancelled(self) -> bool:
        """Return whether cancellation has been requested."""
        return self._event.is_set()

    def raise_if_cancelled(self) -> None:
        """Raise TaskCancelledError if cancellation was requested."""
        if self.is_cancelled:
            raise TaskCancelledError("Task cancellation was requested.")
