"""Provides miscellaneous methods that abstract away common operations or provide functionality not commonly available
from popular Python libraries.
"""

from __future__ import annotations

from os import cpu_count
import re
from typing import TYPE_CHECKING, Any
from functools import lru_cache
from collections.abc import Iterable, Generator

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

from ..console import console

# Default dtype for scalar byte serialization and deserialization functions.
_DEFAULT_SCALAR_DTYPE: np.dtype[Any] = np.dtype("<i8")


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
    # Numpy arrays are processed based on their dimensionality. This has to do with the fact that zero-dimensional
    # numpy arrays are interpreted as scalars by some numpy methods and as arrays by others.
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
    # Unreachable: console.error() is NoReturn, but ruff cannot trace NoReturn through method calls (RET503).
    # noinspection PyUnreachableCode
    raise TypeError(message)  # pragma: no cover


def chunk_iterable(
    iterable: NDArray[Any] | tuple[Any, ...] | list[Any], chunk_size: int
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
    for start_index in range(0, len(iterable), chunk_size):
        chunk_slice = iterable[start_index : start_index + chunk_size]
        yield np.array(chunk_slice) if isinstance(iterable, np.ndarray) else tuple(chunk_slice)


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


def resolve_worker_count(
    requested_workers: int = 0,
    reserved_cores: int = 2,
) -> int:
    """Determines the number of CPU cores to allocate for a processing job.

    Auto-detects available cores, subtracts ``reserved_cores``, and clamps the result to at least 1. A positive
    ``requested_workers`` further caps the result. Any non-positive value requests all available cores.

    Args:
        requested_workers: The maximum number of workers to allocate. Non-positive values request all available cores.
        reserved_cores: The number of cores to reserve for system use. Must be >= 0.

    Returns:
        The number of CPU cores to use, always >= 1.

    Raises:
        ValueError: If ``reserved_cores`` is negative.
    """
    if reserved_cores < 0:
        message = (
            f"Invalid 'reserved_cores' value encountered when resolving worker count. Expected a value >= 0, but "
            f"encountered {reserved_cores}."
        )
        console.error(message=message, error=ValueError)

    # Determine the usable core budget. Falls back to reserved_cores if cpu_count() returns None.
    available = cpu_count()
    if available is None:
        available = reserved_cores
    budget = max(1, available - reserved_cores)

    # If the caller specified a worker cap, respect it against the budget.
    if requested_workers > 0:
        return min(requested_workers, budget)

    return budget


def resolve_parallel_job_capacity(workers_per_job: int) -> int:
    """Determines how many jobs can run in parallel given the per-job core allocation.

    Divides the available core count by ``workers_per_job``, returning at least 1.

    Args:
        workers_per_job: The number of CPU cores each job requires. Must be >= 1.

    Returns:
        The number of parallel jobs that can run concurrently, always >= 1.

    Raises:
        ValueError: If ``workers_per_job`` is less than 1.
    """
    if workers_per_job < 1:
        message = (
            f"Invalid 'workers_per_job' value encountered when resolving parallel job capacity. Expected a value "
            f">= 1, but encountered {workers_per_job}."
        )
        console.error(message=message, error=ValueError)

    available = cpu_count()
    if available is None:
        return 1

    return max(1, available // workers_per_job)


def convert_scalar_to_bytes(
    value: int | float | bool | np.generic,  # noqa: PYI041, FBT001
    dtype: np.dtype[Any] = _DEFAULT_SCALAR_DTYPE,
) -> NDArray[np.uint8]:
    """Serializes a scalar value to an uint8 byte array.

    The returned array length depends on the dtype: 1 byte for uint8/int8/bool, 2 for int16/uint16, 4 for
    int32/uint32/float32, 8 for int64/uint64/float64, etc.

    Notes:
        Uses an internal LRU cache keyed on the ``(value, dtype_str)`` tuple. The cached raw bytes are converted to a
        new numpy array on each call, avoiding mutation issues. This benefits tight loops where the same value+dtype
        pair is serialized repeatedly.

    Args:
        value: The scalar value to serialize.
        dtype: The numpy dtype specifying the target type and byte order.

    Returns:
        A 1D numpy array of dtype uint8 containing the serialized bytes.
    """
    # Converts numpy scalar types to Python scalars for cache key hashability.
    if isinstance(value, np.generic):
        value = value.item()

    raw = _cached_convert_scalar_to_bytes(value, dtype.str)
    return np.frombuffer(raw, dtype=np.uint8).copy()


def convert_bytes_to_scalar(
    data: NDArray[np.uint8],
    dtype: np.dtype[Any] = _DEFAULT_SCALAR_DTYPE,
) -> int | float | bool:
    """Deserializes an uint8 byte array to a Python scalar.

    Args:
        data: A 1D numpy array of dtype uint8 containing the serialized bytes.
        dtype: The numpy dtype specifying the target type and byte order.

    Returns:
        The deserialized Python int, float, or bool value.

    Raises:
        TypeError: If ``data`` is not an uint8 numpy array.
        ValueError: If ``data`` is not 1D or its byte count does not match the target dtype's itemsize.
    """
    if not isinstance(data, np.ndarray) or data.dtype != np.uint8:
        message = (
            f"Invalid 'data' type encountered when converting bytes to scalar. Expected a uint8 numpy array, but "
            f"encountered {type(data).__name__} with dtype {getattr(data, 'dtype', 'N/A')}."
        )
        console.error(message=message, error=TypeError)

    if data.ndim != 1:
        message = (
            f"Invalid 'data' shape encountered when converting bytes to scalar. Expected a 1D array, but encountered "
            f"an array with {data.ndim} dimensions."
        )
        console.error(message=message, error=ValueError)

    if data.nbytes != dtype.itemsize:
        message = (
            f"Invalid 'data' size encountered when converting bytes to scalar. Expected {dtype.itemsize} bytes for "
            f"dtype {dtype}, but encountered {data.nbytes} bytes."
        )
        console.error(message=message, error=ValueError)

    result: int | float | bool = dtype.type(np.frombuffer(data, dtype=dtype)[0]).item()
    return result


def convert_array_to_bytes(array: NDArray[Any]) -> NDArray[np.uint8]:
    """Serializes a 1D numpy array of any supported dtype to an uint8 byte array.

    The ``.copy()`` ensures the returned array is independent of the source array's memory.

    Args:
        array: A 1D, non-empty numpy array to serialize.

    Returns:
        A 1D numpy array of dtype uint8 containing the serialized bytes.

    Raises:
        ValueError: If ``array`` is not 1D or is empty.
    """
    if array.ndim != 1:
        message = (
            f"Invalid 'array' shape encountered when converting array to bytes. Expected a 1D array, but encountered "
            f"an array with {array.ndim} dimensions."
        )
        console.error(message=message, error=ValueError)

    if array.size == 0:
        message = "Invalid 'array' size encountered when converting array to bytes. Expected a non-empty array."
        console.error(message=message, error=ValueError)

    return np.frombuffer(array, dtype=np.uint8).copy()


def convert_bytes_to_array(
    data: NDArray[np.uint8],
    dtype: np.dtype[Any],
) -> NDArray[Any]:
    """Deserializes an uint8 byte array to a typed numpy array.

    Args:
        data: A 1D numpy array of dtype uint8 containing the serialized bytes.
        dtype: The numpy dtype specifying the target element type and byte order.

    Returns:
        A 1D numpy array of the specified dtype containing the deserialized values.

    Raises:
        ValueError: If ``data`` is not 1D or its byte count is not evenly divisible by the target dtype's itemsize.
    """
    if data.ndim != 1:
        message = (
            f"Invalid 'data' shape encountered when converting bytes to array. Expected a 1D array, but encountered "
            f"an array with {data.ndim} dimensions."
        )
        console.error(message=message, error=ValueError)

    if data.nbytes % dtype.itemsize != 0:
        message = (
            f"Invalid 'data' size encountered when converting bytes to array. The byte count ({data.nbytes}) is not "
            f"evenly divisible by the target dtype itemsize ({dtype.itemsize}) for dtype {dtype}."
        )
        console.error(message=message, error=ValueError)

    return np.frombuffer(data, dtype=dtype).copy()


@lru_cache(maxsize=4096)
def _cached_convert_scalar_to_bytes(value: int | float | bool, dtype_str: str) -> bytes:  # noqa: PYI041, FBT001
    """Serializes a scalar value to raw bytes using an LRU cache.

    Args:
        value: The scalar value to serialize.
        dtype_str: The numpy dtype string specifying the target type and byte order.

    Returns:
        The raw bytes representing the serialized scalar.
    """
    return np.array([value], dtype=dtype_str).view(np.uint8).tobytes()
