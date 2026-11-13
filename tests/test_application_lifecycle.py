
import pytest

from modlens.core.application_lifecycle import (
    ApplicationLifecycle,
    LifecycleState,
)
from modlens.core.exceptions import (
    ApplicationLifecycleError,
    ApplicationShutdownError,
    ApplicationStartupError,
)


def test_initial_state_is_created() -> None:
    lifecycle = ApplicationLifecycle()

    assert lifecycle.state is LifecycleState.CREATED


def test_startup_steps_execute_in_registration_order() -> None:
    lifecycle = ApplicationLifecycle()
    execution_order: list[str] = []

    lifecycle.add_step(
        "First",
        lambda: execution_order.append("first"),
    )
    lifecycle.add_step(
        "Second",
        lambda: execution_order.append("second"),
    )

    lifecycle.start()

    assert execution_order == ["first", "second"]
    assert lifecycle.state is LifecycleState.RUNNING


def test_shutdown_executes_cleanup_in_reverse_order() -> None:
    lifecycle = ApplicationLifecycle()
    cleanup_order: list[str] = []

    lifecycle.add_step(
        "First",
        lambda: lambda: cleanup_order.append("first"),
    )
    lifecycle.add_step(
        "Second",
        lambda: lambda: cleanup_order.append("second"),
    )

    lifecycle.start()
    lifecycle.shutdown()

    assert cleanup_order == ["second", "first"]
    assert lifecycle.state is LifecycleState.STOPPED


def test_startup_failure_rolls_back_completed_steps() -> None:
    lifecycle = ApplicationLifecycle()
    cleanup_order: list[str] = []

    def fail_startup() -> None:
        raise RuntimeError("Database initialization failed.")

    lifecycle.add_step(
        "First",
        lambda: lambda: cleanup_order.append("first"),
    )
    lifecycle.add_step(
        "Database Initialization",
        fail_startup,
    )

    with pytest.raises(ApplicationStartupError) as exc_info:
        lifecycle.start()

    assert "Database Initialization" in str(exc_info.value)
    assert cleanup_order == ["first"]
    assert lifecycle.state is LifecycleState.FAILED
    assert isinstance(exc_info.value.__cause__, RuntimeError)


def test_startup_failure_attempts_all_rollback_callbacks() -> None:
    lifecycle = ApplicationLifecycle()
    cleanup_order: list[str] = []

    def failing_cleanup() -> None:
        cleanup_order.append("second")
        raise RuntimeError("Cleanup failed.")

    def fail_startup() -> None:
        raise RuntimeError("Startup failed.")

    lifecycle.add_step(
        "First",
        lambda: lambda: cleanup_order.append("first"),
    )
    lifecycle.add_step(
        "Second",
        lambda: failing_cleanup,
    )
    lifecycle.add_step("Failure", fail_startup)

    with pytest.raises(ApplicationStartupError) as exc_info:
        lifecycle.start()

    assert cleanup_order == ["second", "first"]
    assert "Cleanup also encountered errors" in str(exc_info.value)
    assert lifecycle.state is LifecycleState.FAILED


def test_shutdown_attempts_all_callbacks_when_one_fails() -> None:
    lifecycle = ApplicationLifecycle()
    cleanup_order: list[str] = []

    def failing_cleanup() -> None:
        cleanup_order.append("second")
        raise RuntimeError("Second cleanup failed.")

    lifecycle.add_step(
        "First",
        lambda: lambda: cleanup_order.append("first"),
    )
    lifecycle.add_step(
        "Second",
        lambda: failing_cleanup,
    )
    lifecycle.add_step(
        "Third",
        lambda: lambda: cleanup_order.append("third"),
    )

    lifecycle.start()

    with pytest.raises(ApplicationShutdownError):
        lifecycle.shutdown()

    assert cleanup_order == ["third", "second", "first"]
    assert lifecycle.state is LifecycleState.STOPPED


def test_repeated_shutdown_is_safe() -> None:
    lifecycle = ApplicationLifecycle()
    cleanup_count = 0

    def cleanup() -> None:
        nonlocal cleanup_count
        cleanup_count += 1

    lifecycle.add_step("First", lambda: cleanup)
    lifecycle.start()

    lifecycle.shutdown()
    lifecycle.shutdown()

    assert cleanup_count == 1
    assert lifecycle.state is LifecycleState.STOPPED


def test_startup_cannot_run_more_than_once() -> None:
    lifecycle = ApplicationLifecycle()

    lifecycle.start()

    with pytest.raises(ApplicationLifecycleError):
        lifecycle.start()


def test_steps_cannot_be_added_after_startup() -> None:
    lifecycle = ApplicationLifecycle()
    lifecycle.start()

    with pytest.raises(ApplicationLifecycleError):
        lifecycle.add_step("Late Step", lambda: None)


def test_duplicate_startup_step_names_are_rejected() -> None:
    lifecycle = ApplicationLifecycle()

    lifecycle.add_step("Database", lambda: None)

    with pytest.raises(ApplicationLifecycleError):
        lifecycle.add_step("Database", lambda: None)


def test_shutdown_before_startup_is_safe() -> None:
    lifecycle = ApplicationLifecycle()

    lifecycle.shutdown()

    assert lifecycle.state is LifecycleState.STOPPED


def test_shutdown_after_startup_failure_is_safe() -> None:
    lifecycle = ApplicationLifecycle()
    cleanup_count = 0

    def cleanup() -> None:
        nonlocal cleanup_count
        cleanup_count += 1

    def fail_startup() -> None:
        raise RuntimeError("Startup failed.")

    lifecycle.add_step("First", lambda: cleanup)
    lifecycle.add_step("Failure", fail_startup)

    with pytest.raises(ApplicationStartupError):
        lifecycle.start()

    assert lifecycle.state is LifecycleState.FAILED
    assert cleanup_count == 1

    lifecycle.shutdown()

    assert lifecycle.state is LifecycleState.STOPPED
    assert cleanup_count == 1
