
"""Framework-neutral interfaces for ModLens services."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Logger(Protocol):
    """Minimal logging interface required by ModLens services."""

    def debug(self, message: object, *args: object, **kwargs: object) -> None:
        ...

    def info(self, message: object, *args: object, **kwargs: object) -> None:
        ...

    def warning(self, message: object, *args: object, **kwargs: object) -> None:
        ...

    def error(self, message: object, *args: object, **kwargs: object) -> None:
        ...

    def exception(self, message: object, *args: object, **kwargs: object) -> None:
        ...
