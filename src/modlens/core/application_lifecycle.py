
"""Coordinates ordered application startup and graceful shutdown."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto

from modlens.core.exceptions import (
    ApplicationLifecycleError,
    ApplicationShutdownError,
    ApplicationStartupError,
)


class LifecycleState(Enum):
    """Possible states of the application lifecycle."""

    CREATED = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()
    FAILED = auto()


@dataclass(frozen=True)
class StartupStep:
    """A named startup operation and its optional cleanup callback."""

    name: str
    initialize: Callable[[], Callable[[], None] | None]


class ApplicationLifecycle:
    """Run startup operations in order and clean them up in reverse order."""

    def __init__(self) -> None:
        self._steps: list[StartupStep] = []
        self._cleanup_callbacks: list[Callable[[], None]] = []
        self._state = LifecycleState.CREATED

    @property
    def state(self) -> LifecycleState:
        """Return the current lifecycle state."""
        return self._state

    def add_step(
        self,
        name: str,
        initialize: Callable[[], Callable[[], None] | None],
    ) -> None:
        """Register a startup operation before startup begins."""
        if self._state is not LifecycleState.CREATED:
            raise ApplicationLifecycleError(
                "Startup steps cannot be added after startup has begun."
            )

        if not name.strip():
            raise ApplicationLifecycleError(
                "A startup step must have a non-empty name."
            )

        if any(step.name == name for step in self._steps):
            raise ApplicationLifecycleError(
                f"Startup step '{name}' is already registered."
            )

        if not callable(initialize):
            raise ApplicationLifecycleError(
                "A startup step must have a callable initializer."
            )

        self._steps.append(StartupStep(name, initialize))

    def start(self) -> None:
        """Run all registered startup operations in registration order."""
        if self._state is not LifecycleState.CREATED:
            raise ApplicationLifecycleError(
                "Application startup can only run once."
            )

        self._state = LifecycleState.STARTING
        current_step = "unknown"

        try:
            for step in self._steps:
                current_step = step.name
                cleanup = step.initialize()

                if cleanup is not None:
                    if not callable(cleanup):
                        raise TypeError(
                            f"Startup step '{step.name}' returned "
                            "a non-callable cleanup operation."
                        )
                    self._cleanup_callbacks.append(cleanup)

        except Exception as exc:
            cleanup_errors = self._run_cleanup_callbacks()
            self._state = LifecycleState.FAILED

            message = f"Application startup failed during step '{current_step}'."

            if cleanup_errors:
                details = "; ".join(str(error) for error in cleanup_errors)
                message += f" Cleanup also encountered errors: {details}"

            raise ApplicationStartupError(message) from exc

        self._state = LifecycleState.RUNNING

    def shutdown(self) -> None:
        """Run all registered cleanup operations in reverse order."""
        if self._state is LifecycleState.STOPPED:
            return

        if self._state in {
            LifecycleState.STARTING,
            LifecycleState.STOPPING,
        }:
            raise ApplicationLifecycleError(
                "Application shutdown cannot run in the current state."
            )

        self._state = LifecycleState.STOPPING
        cleanup_errors = self._run_cleanup_callbacks()
        self._state = LifecycleState.STOPPED

        if cleanup_errors:
            details = "; ".join(str(error) for error in cleanup_errors)
            raise ApplicationShutdownError(
                f"Application shutdown encountered errors: {details}"
            )

    def _run_cleanup_callbacks(self) -> list[Exception]:
        """Attempt every cleanup operation in reverse registration order."""
        callbacks = list(reversed(self._cleanup_callbacks))
        self._cleanup_callbacks.clear()

        errors: list[Exception] = []

        for cleanup in callbacks:
            try:
                cleanup()
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)

        return errors
