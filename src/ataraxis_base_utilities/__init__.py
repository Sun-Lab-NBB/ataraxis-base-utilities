"""This library exposes a minimalistic set of shared utility functions used to support other projects.

This library has a very broad scope: it centralizes widely shared functionality used across multiple
Sun Lab projects. Any function reused by more than 5 other projects becomes a candidate for inclusion into this library.

Currently, the library provides the following functionality:
- Console: A class that provides message and error printing and logging functionality.

While this library is explicitly configured to work with other Sun Lab projects, it can be adapted to work for non-lab
projects. Specifically, this would likely require changing default argument values used by functions exposed through
this library.
"""

from .console import Console, LogLevel, LogBackends, LogExtensions

# Preconfigures and exposes Console class instance as a variable, similar to how Loguru exposes logger. This instance
# can be used globally instead of defining a custom console variable.
console: Console = Console(logger_backend=LogBackends.LOGURU)

__all__ = ["console", "Console", "LogLevel", "LogBackends", "LogExtensions"]
