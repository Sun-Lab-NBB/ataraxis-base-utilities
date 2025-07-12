"""This library exposes a minimalistic set of shared utility classes and functions used to support other projects.

See https://github.com/Sun-Lab-NBB/ataraxis-base-utilities for more details.
API documentation: https://ataraxis-base-utilities-api-docs.netlify.app/
Author: Ivan Kondratyev (Inkaros)
"""

from .console import (
    Console,
    LogLevel,
    LogBackends,
    LogExtensions,
    pass_callback,
    default_callback,
    ensure_directory_exists,
)
from .standalone_methods import ensure_list, error_format, chunk_iterable, check_condition, compare_nested_tuples

# Preconfigures and exposes Console class instance as a variable, similar to how Loguru exposes logger. This instance
# can be used globally instead of defining a custom console variable.
console: Console = Console(logger_backend=LogBackends.LOGURU, auto_handles=True, use_default_error_handler=True)

__all__ = [
    "console",
    "Console",
    "LogLevel",
    "LogBackends",
    "LogExtensions",
    "ensure_list",
    "compare_nested_tuples",
    "chunk_iterable",
    "check_condition",
    "default_callback",
    "ensure_directory_exists",
    "error_format",
    "pass_callback",
]
