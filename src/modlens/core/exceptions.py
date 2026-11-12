"""Application-level exception hierarchy for ModLens.

Keep these exceptions focused on failures the application can meaningfully
handle. Third-party validation exceptions are not shadowed or redefined here.
"""


class ModLensError(Exception):
    """Base exception for expected, user-actionable ModLens failures."""


class ConfigurationError(ModLensError):
    """Configuration could not be loaded, parsed, or applied."""


class DatabaseError(ModLensError):
    """A database operation failed."""


class MigrationError(DatabaseError):
    """A database schema migration failed."""


class DiscoveryError(ModLensError):
    """A discovery operation failed."""


class RegistryAccessError(DiscoveryError):
    """The operating-system registry could not be accessed."""


class PathAccessError(DiscoveryError):
    """A required filesystem path could not be accessed."""


class ParseError(DiscoveryError):
    """A discovery source could not be parsed."""


class ServiceRegistryError(ModLensError):
    """Base exception for service registry failures."""


class DuplicateServiceError(ServiceRegistryError):
    """A service is already registered for the requested interface."""


class ServiceNotFoundError(ServiceRegistryError):
    """No service is registered for the requested interface."""


class InvalidServiceRegistrationError(ServiceRegistryError):
    """A service does not satisfy its declared registration interface."""
    

class ApplicationLifecycleError(ModLensError):
    """Base exception for application lifecycle failures."""


class ApplicationStartupError(ApplicationLifecycleError):
    """Application startup could not complete."""


class ApplicationShutdownError(ApplicationLifecycleError):
    """One or more application shutdown operations failed."""
