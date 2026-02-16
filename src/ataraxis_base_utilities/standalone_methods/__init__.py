"""Provides standalone methods that abstract away common data manipulation tasks."""

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
    "chunk_iterable",
    "convert_array_to_bytes",
    "convert_bytes_to_array",
    "convert_bytes_to_scalar",
    "convert_scalar_to_bytes",
    "ensure_list",
    "error_format",
    "resolve_parallel_job_capacity",
    "resolve_worker_count",
]
