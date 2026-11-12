"""Tests for cooperative task cancellation."""

from threading import Thread

import pytest

from modlens.core.cancellation import CancellationToken
from modlens.core.exceptions import ModLensError, TaskCancelledError


def test_token_starts_not_cancelled() -> None:
    token = CancellationToken()

    assert token.is_cancelled is False


def test_cancel_sets_cancellation_state() -> None:
    token = CancellationToken()

    token.cancel()

    assert token.is_cancelled is True


def test_repeated_cancel_is_safe() -> None:
    token = CancellationToken()

    token.cancel()
    token.cancel()

    assert token.is_cancelled is True


def test_cancellation_state_cannot_be_reset() -> None:
    token = CancellationToken()

    token.cancel()

    assert token.is_cancelled is True


def test_raise_if_cancelled_does_nothing_before_cancellation() -> None:
    token = CancellationToken()

    token.raise_if_cancelled()


def test_raise_if_cancelled_raises_after_cancellation() -> None:
    token = CancellationToken()
    token.cancel()

    with pytest.raises(TaskCancelledError):
        token.raise_if_cancelled()


def test_cancellation_exception_is_a_modlens_error() -> None:
    token = CancellationToken()
    token.cancel()

    with pytest.raises(ModLensError):
        token.raise_if_cancelled()


def test_cancellation_can_be_requested_from_another_thread() -> None:
    token = CancellationToken()

    thread = Thread(target=token.cancel)
    thread.start()
    thread.join()

    assert token.is_cancelled is True


def test_cancellation_is_visible_across_threads() -> None:
    token = CancellationToken()
    observed_states: list[bool] = []

    def observe_cancellation() -> None:
        observed_states.append(token.is_cancelled)

    token.cancel()

    thread = Thread(target=observe_cancellation)
    thread.start()
    thread.join()

    assert observed_states == [True]
