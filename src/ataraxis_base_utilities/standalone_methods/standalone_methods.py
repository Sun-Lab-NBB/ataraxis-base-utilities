"""This module contains miscellaneous methods that either abstract away common operations to reduce boilerplate code or
provide functionality not commonly available from popular Python libraries.
"""

import re
from typing import Any
from collections.abc import Iterable, Generator

import numpy as np
from numpy.typing import NDArray

from ..console import console


def ensure_list(
    input_item: Any,
) -> list[Any]:
    """Ensures that the input object is returned as a list.

    If the object is not already a list, attempts to convert it into a list. If the object is a list, returns the
    object unchanged.

    Args:
        input_item: The object to be converted into or preserved as a Python list.

    Returns:
        The object converted to a Python list datatype.

    Raises:
        TypeError: If the input object cannot be converted to a list.
    """
    # Scalars are added to a list and returned as a one-item list. Scalars are handled first to avoid clashing with
    # iterable types.
    if np.isscalar(input_item) or input_item is None:  # Covers Python scalars and NumPy scalars
        return [input_item]
    # Numpy arrays are processed based on their dimensionality. This has to dow tih the fact that zero-dimensional
    # numpy arrays are interpreted as scalars by some numpy methods and as array by others.
    if isinstance(input_item, np.ndarray):
        # 1+-dimensional arrays are processed via tolist(), which correctly casts them to Python list format.
        if input_item.size > 1 and input_item.ndim >= 1:
            output_list: list[Any] = input_item.tolist()
            return output_list
        if input_item.size == 1:
            # 0-dimensional arrays are essentially scalars, so the data is popped out via item() and is wrapped
            # into a list.
            return [input_item.item()]
    # Lists are returned as-is, without any further modification.
    if isinstance(input_item, list):
        return input_item
    # Iterable types are converted via list() method.
    if isinstance(input_item, Iterable):
        return list(input_item)
    # Catch-all type error to execute if the input is not supported.
    message = (
        f"Unable to convert the input item to a Python list, as items of type {type(input_item).__name__} "
        f"are not supported."
    )
    console.error(message=message, error=TypeError)
    # This is just to appease mypy.
    raise TypeError(message)  # pragma: no cover


# noinspection PyTypeHints
def chunk_iterable(
    iterable: NDArray[Any] | tuple[Any] | list[Any], chunk_size: int
) -> Generator[tuple[Any, ...] | NDArray[Any], None, None]:
    """Yields successive chunks from the input ordered Python iterable or NumPy array.

    Notes:
        For NumPy arrays, the function maintains the original data type and dimensionality, returning NumPy array
        chunks. For other iterables, it always returns chunks as tuples.

        The last yielded chunk contains any leftover elements if the iterable's length is not evenly divisible by
        chunk_size. This last chunk may be smaller than all other chunks.

    Args:
        iterable: The Python iterable or NumPy array to split into chunks.
        chunk_size: The maximum number of elements in each chunk.

    Raises:
        TypeError: If 'iterable' is not of a correct type.
        ValueError: If 'chunk_size' value is below 1.

    Yields:
        Chunks of the input iterable (as a tuple) or NumPy array, containing at most chunk_size elements.
    """
    if not isinstance(iterable, (np.ndarray, list, tuple)):
        message: str = (
            f"Unsupported 'iterable' type encountered when chunking iterable. Expected a list, tuple or numpy array, "
            f"but encountered {iterable} of type {type(iterable).__name__}."
        )
        console.error(message=message, error=TypeError)

    if chunk_size < 1:
        message = (
            f"Unsupported 'chunk_size' value encountered when chunking iterable. Expected a positive non-zero value, "
            f"but encountered {chunk_size}."
        )
        console.error(message=message, error=ValueError)

    # Chunking is performed along the first dimension for both NumPy arrays and Python iterable sequences.
    # This preserves array dimensionality within chunks for NumPy arrays.
    for chunk in range(0, len(iterable), chunk_size):
        chunk_slice = iterable[chunk : chunk + chunk_size]
        yield np.array(chunk_slice) if isinstance(iterable, np.ndarray) else tuple(chunk_slice)


# noinspection PyProtectedMember
def error_format(message: str) -> str:
    """Formats the input message to match the default Console format and escapes it using re, so that it can be used to
    verify raised exceptions.

    Notes:
        This method is primarily designed to help developers writing test functions for the Ataraxis codebase.

        This method directly accesses the global console variable to retrieve the formatting parameters. Therefore, it
        always matches the configuration used by the Console class.

    Args:
        message: The message to format.

    Returns:
        The formatted message.
    """
    return re.escape(console.format_message(message=message, loguru=False))
