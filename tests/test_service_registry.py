
import logging
from typing import Protocol, runtime_checkable

import pytest

from modlens.core.exceptions import (
    DuplicateServiceError,
    InvalidServiceRegistrationError,
    ServiceNotFoundError,
    ServiceRegistryError,
)
from modlens.core.interfaces import Logger
from modlens.core.service_registry import ServiceRegistry


@runtime_checkable
class ExampleService(Protocol):
    def execute(self) -> str:
        ...


class ExampleServiceImplementation:
    def execute(self) -> str:
        return "executed"


class AnotherService:
    def execute(self) -> str:
        return "another"


class IncompatibleService:
    def other_method(self) -> str:
        return "incompatible"


def test_register_and_retrieve_service():
    registry = ServiceRegistry()
    service = ExampleServiceImplementation()

    registry.register(ExampleService, service)

    assert registry.get(ExampleService) is service


def test_multiple_independent_services_can_be_registered():
    registry = ServiceRegistry()
    first = ExampleServiceImplementation()
    second = AnotherService()

    registry.register(ExampleService, first)
    registry.register(AnotherService, second)

    assert registry.get(ExampleService) is first
    assert registry.get(AnotherService) is second


def test_duplicate_registration_is_rejected():
    registry = ServiceRegistry()
    first = ExampleServiceImplementation()

    registry.register(ExampleService, first)

    with pytest.raises(DuplicateServiceError):
        registry.register(ExampleService, ExampleServiceImplementation())

    assert registry.get(ExampleService) is first


def test_missing_service_raises_clear_exception():
    registry = ServiceRegistry()

    with pytest.raises(ServiceNotFoundError):
        registry.get(ExampleService)


def test_optional_retrieval_returns_none_when_missing():
    registry = ServiceRegistry()

    assert registry.get_optional(ExampleService) is None


def test_optional_retrieval_returns_registered_service():
    registry = ServiceRegistry()
    service = ExampleServiceImplementation()
    registry.register(ExampleService, service)

    assert registry.get_optional(ExampleService) is service


def test_has_reports_registration_state():
    registry = ServiceRegistry()

    assert registry.has(ExampleService) is False

    registry.register(ExampleService, ExampleServiceImplementation())

    assert registry.has(ExampleService) is True


def test_unregister_removes_service():
    registry = ServiceRegistry()
    service = ExampleServiceImplementation()
    registry.register(ExampleService, service)

    assert registry.unregister(ExampleService) is True
    assert registry.has(ExampleService) is False
    assert registry.get_optional(ExampleService) is None


def test_unregister_missing_service_returns_false():
    registry = ServiceRegistry()

    assert registry.unregister(ExampleService) is False


def test_incompatible_service_is_rejected():
    registry = ServiceRegistry()

    with pytest.raises(InvalidServiceRegistrationError):
        registry.register(ExampleService, IncompatibleService())


def test_non_runtime_checkable_protocol_is_rejected():
    class NonRuntimeProtocol(Protocol):
        def execute(self) -> str:
            ...

    registry = ServiceRegistry()

    with pytest.raises(InvalidServiceRegistrationError):
        registry.register(NonRuntimeProtocol, ExampleServiceImplementation())


def test_non_type_interface_is_rejected():
    registry = ServiceRegistry()

    with pytest.raises(InvalidServiceRegistrationError):
        registry.register("ExampleService", ExampleServiceImplementation())


def test_none_service_is_rejected():
    registry = ServiceRegistry()

    with pytest.raises(InvalidServiceRegistrationError):
        registry.register(object, None)


def test_standard_logging_logger_satisfies_logger_interface():
    registry = ServiceRegistry()
    logger = logging.getLogger("modlens.test")

    registry.register(Logger, logger)

    assert registry.get(Logger) is logger


def test_registry_exceptions_share_common_base():
    assert issubclass(DuplicateServiceError, ServiceRegistryError)
    assert issubclass(ServiceNotFoundError, ServiceRegistryError)
    assert issubclass(InvalidServiceRegistrationError, ServiceRegistryError)
