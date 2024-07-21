from .console_class import (
    Console as Console,
    LogLevel as LogLevel,
    LogBackends as LogBackends,
    LogExtensions as LogExtensions,
    default_callback as default_callback,
)

__all__ = ["console", "Console", "LogLevel", "LogBackends", "LogExtensions", "default_callback"]

console: Console
