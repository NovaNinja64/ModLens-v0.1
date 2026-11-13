
"""Thread-safe registry for application services.

The registry protects its own mapping operations. It does not guarantee
that registered service instances are themselves thread-safe."""

from __future__ import annotations

from threading import RLock
from typing import TypeVar

from modlens.core.exceptions import (
    DuplicateServiceError,
    InvalidServiceRegistrationError,
    ServiceNotFoundError,
)

T = TypeVar("T")


class ServiceRegistry:
    """Register and retrieve service instances by interface type."""

    def __init__(self) -> None:
        self._services: dict[type[object], object] = {}
        self._lock = RLock()

    def register(self, interface: type[T], service: T) -> None:
        """Register a service for an interface without replacing existing entries.

        Runtime validation checks that the service is an instance of the
        supplied class or runtime-checkable protocol. For protocols, Python
        checks member presence, not method signatures or type compatibility.
        """
        if not isinstance(interface, type):
            raise InvalidServiceRegistrationError(
                "The registration interface must be a class or protocol."
            )
        
        if service is None:
            raise InvalidServiceRegistrationError(
                "A registered service cannot be None."
            )
        
        try:
            is_compatible = isinstance(service, interface)
        except TypeError as exc:
            raise InvalidServiceRegistrationError(
                "The interface must support runtime instance checks. "
                "Protocols must use @runtime_checkable."
            ) from exc

        if not is_compatible:
            raise InvalidServiceRegistrationError(
                f"Service {type(service).__name__} does not satisfy "
                f"interface {interface.__name__}."
            )

        with self._lock:
            if interface in self._services:
                raise DuplicateServiceError(
                    f"A service is already registered for {interface.__name__}."
                )
            self._services[interface] = service

    def get(self, interface: type[T]) -> T:
        """Return the registered service or raise if it is missing."""
        with self._lock:
            try:
                service = self._services[interface]
            except KeyError as exc:
                raise ServiceNotFoundError(
                    f"No service is registered for {interface.__name__}."
                ) from exc

        return service  # type: ignore[return-value]

    def get_optional(self, interface: type[T]) -> T | None:
        """Return the registered service, or None when it is missing."""
        with self._lock:
            service = self._services.get(interface)

        return service  # type: ignore[return-value]

    def has(self, interface: type[object]) -> bool:
        """Return whether a service is registered for the interface."""
        with self._lock:
            return interface in self._services

    def unregister(self, interface: type[object]) -> bool:
        """Remove a service registration.

        Returns True when an entry was removed, or False when none existed.
        """
        with self._lock:
            if interface not in self._services:
                return False
            del self._services[interface]
            return True
