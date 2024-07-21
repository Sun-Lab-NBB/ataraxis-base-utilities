"""This library exposes a minimalistic set of shared utility classes and functions used to support other projects.

This library has a very broad scope: it centralizes widely shared functionality used across multiple
Sun Lab projects. Any class or function reused by more than 5 other projects becomes a candidate for inclusion into
this library.

Currently, the library provides the following functionality:
- Console: A class that provides message and error printing and logging functionality.
- ensure_list: A function that ensures that an input is a list, converting a wide range of non-list inputs into python
list types if necessary.
- compare_nested_tuples: A function that compares two-dimensional nested tuples, handling cases not suitable for
numpy 'array_equal' method.
- chunk_iterable: A function that chunks the input iterable into equal-sized chunk of the requested size.
- check_condition: A function that evaluates whether two input values satisfy a certain logical condition, uch as
equality.

While this library is explicitly configured to work with other Sun Lab projects, it can be adapted to work for non-lab
projects. Specifically, this would likely require changing default argument values used by functions exposed through
this library.
"""

from .console import Console, LogLevel, LogBackends, LogExtensions, default_callback
from .standalone_methods import ensure_list, chunk_iterable, check_condition, compare_nested_tuples

# Preconfigures and exposes Console class instance as a variable, similar to how Loguru exposes logger. This instance
# can be used globally instead of defining a custom console variable.
console: Console = Console(logger_backend=LogBackends.LOGURU, auto_handles=True)

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
]
