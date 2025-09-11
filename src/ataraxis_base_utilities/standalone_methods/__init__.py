"""This package provides standalone methods that abstract away common data manipulation tasks."""

from .standalone_methods import ensure_list, error_format, chunk_iterable

__all__ = ["chunk_iterable", "ensure_list", "error_format"]
