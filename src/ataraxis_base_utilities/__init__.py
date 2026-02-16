"""Provides shared utility assets used to support most other Sun (NeuroAI) lab projects.

See the `documentation <https://ataraxis-base-utilities-api-docs.netlify.app/>`_ for the description of available
assets. See the `source code repository <https://github.com/Sun-Lab-NBB/ataraxis-base-utilities>`_ for more details.

Authors: Ivan Kondratyev (Inkaros)
"""

from .console import Console, LogLevel, LogFormats, console, ensure_directory_exists
from .standalone_methods import ensure_list, error_format, chunk_iterable

__all__ = [
    "Console",
    "LogFormats",
    "LogLevel",
    "chunk_iterable",
    "console",
    "ensure_directory_exists",
    "ensure_list",
    "error_format",
]
