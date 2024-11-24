"""This package provides a range of standalone methods that abstract away common data manipulation tasks.

The methods exposed through this package broadly fulfill two functions. Primarily, they aggregate boilerplate code
routinely reused for various processing tasks, such as converting a wide range of inputs into a python list.
Additionally, some methods provide unique functionality not covered by other libraries commonly available to our
projects, such as comparing two-dimensional tuples with mixed element datatypes and sub-tuple topology.

See standalone_methods.py module for more details about the standalone methods provided by this package.
"""

from .standalone_methods import ensure_list, error_format, chunk_iterable, check_condition, compare_nested_tuples

__all__ = ["ensure_list", "compare_nested_tuples", "chunk_iterable", "check_condition", "error_format"]
