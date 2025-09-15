"""This package provides the Console class that exposes methods for writing messages and errors to terminal and
log files.
"""

from .console_class import Console, LogLevel, LogFormats, console, ensure_directory_exists

__all__ = [
    "Console",
    "LogFormats",
    "LogLevel",
    "console",
    "ensure_directory_exists",
]
