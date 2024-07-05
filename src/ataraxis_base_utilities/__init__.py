"""This library exposes widely used utility classes and functions to be shared by the rest of project Ataraxis
modules.

The library does not have specialization beyond focusing on truly ubiquitous functionality that is likely to
be required for almost all if not all well-formed projects. It can be used by non-Ataraxis projects, but will likely
require additional configurations, as most modules from this library come with default Ataraxis parameters hardcoded in
many places.
"""

from .utilities import Console, LogLevel, LogBackends

# Preconfigures and exposes Console class instance as a variable, similar to how Loguru exposes logger. This instance
# can be used globally instead of defining a custom console variable.
console: Console = Console(logger_backend=LogBackends.LOGURU)

__all__ = ["console", "Console", "LogLevel", "LogBackends"]
