from modlens.core.cancellation import CancellationToken
from modlens.core.exceptions import TaskCancelledError
from modlens.core.tasks import FunctionTask


def test_function_task_emits_result_and_lifecycle_signals():
    events = []
    task = FunctionTask(lambda: 42)

    task.signals.started.connect(lambda: events.append("started"))
    task.signals.result.connect(lambda value: events.append(value))
    task.signals.finished.connect(lambda: events.append("finished"))

    task.run()

    assert events == ["started", 42, "finished"]


def test_function_task_emits_failure():
    failures = []
    finished = []
    task = FunctionTask(
        lambda: (_ for _ in ()).throw(ValueError("test error"))
    )

    task.signals.failed.connect(failures.append)
    task.signals.finished.connect(lambda: finished.append(True))

    task.run()

    assert failures == ["ValueError: test error"]
    assert finished == [True]


def test_function_task_skips_execution_when_already_cancelled():
    token = CancellationToken()
    token.cancel()
    executed = []
    cancelled = []
    finished = []

    task = FunctionTask(
        lambda: executed.append(True),
        cancellation_token=token,
    )

    task.signals.cancelled.connect(lambda: cancelled.append(True))
    task.signals.finished.connect(lambda: finished.append(True))

    task.run()

    assert executed == []
    assert cancelled == [True]
    assert finished == [True]


def test_function_task_emits_cancelled_when_callable_detects_cancellation():
    cancelled = []
    finished = []

    def work(cancellation_token):
        cancellation_token.cancel()
        cancellation_token.raise_if_cancelled()

    task = FunctionTask(work, pass_cancellation_token=True)

    task.signals.cancelled.connect(lambda: cancelled.append(True))
    task.signals.finished.connect(lambda: finished.append(True))

    task.run()

    assert cancelled == [True]
    assert finished == [True]


def test_function_task_passes_token_when_requested():
    received_tokens = []
    token = CancellationToken()

    def work(*, cancellation_token):
        received_tokens.append(cancellation_token)
        return "complete"

    task = FunctionTask(
        work,
        cancellation_token=token,
        pass_cancellation_token=True,
    )

    task.run()

    assert received_tokens == [token]


def test_function_task_preserves_existing_callable_compatibility():
    results = []
    task = FunctionTask(lambda value: value * 2, 5)

    task.signals.result.connect(results.append)

    task.run()

    assert results == [10]


def test_function_task_handles_task_cancelled_error():
    cancelled = []

    def work():
        raise TaskCancelledError("cancelled by test")

    task = FunctionTask(work)
    task.signals.cancelled.connect(lambda: cancelled.append(True))

    task.run()

    assert cancelled == [True]
