"""Provides shared utility assets used to support most other Sun (NeuroAI) lab projects.

See the `documentation <https://ataraxis-base-utilities-api-docs.netlify.app/>`_ for the description of available
assets. See the `source code repository <https://github.com/Sun-Lab-NBB/ataraxis-base-utilities>`_ for more details.

Authors: Ivan Kondratyev (Inkaros)
"""

from .console import Console, LogLevel, LogFormats, ProgressBar, console, ensure_directory_exists
from .standalone_methods import (
    ensure_list,
    error_format,
    chunk_iterable,
    resolve_worker_count,
    convert_array_to_bytes,
    convert_bytes_to_array,
    convert_bytes_to_scalar,
    convert_scalar_to_bytes,
    resolve_parallel_job_capacity,
)

__all__ = [
    "Console",
    "LogFormats",
    "LogLevel",
    "ProgressBar",
    "chunk_iterable",
    "console",
    "convert_array_to_bytes",
    "convert_bytes_to_array",
    "convert_bytes_to_scalar",
    "convert_scalar_to_bytes",
    "ensure_directory_exists",
    "ensure_list",
    "error_format",
    "resolve_parallel_job_capacity",
    "resolve_worker_count",
]
