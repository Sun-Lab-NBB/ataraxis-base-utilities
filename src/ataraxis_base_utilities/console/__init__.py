"""This package provides the Console class that exposes methods for writing messages and errors to terminal and
log files.

Additionally, it exposes helper classes and methods used to interface with the main Console class and the 'console'
variable that stores a preconfigured Console class instance. The variable is designed to be shared between all other
libraries to centralize Console API access and control logging parameters through the shared API configuration.

See the console_class.py module for more details about the Console and helper class.
"""

from .console_class import Console, LogLevel, LogBackends, LogExtensions, default_callback

# Preconfigures and exposes Console class instance as a variable, similar to how Loguru exposes logger. This instance
# can be used globally instead of defining a custom console variable.
console: Console = Console(logger_backend=LogBackends.LOGURU, auto_handles=True)

__all__ = ["console", "Console", "LogLevel", "LogBackends", "LogExtensions", "default_callback"]
