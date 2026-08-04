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

from ..console import console

if TYPE_CHECKING:
    from numpy.typing import NDArray

_DEFAULT_SCALAR_DTYPE: np.dtype[Any] = np.dtype("<i8")
"""The default dtype for scalar byte serialization and deserialization functions."""


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
    if np.isscalar(input_item) or input_item is None:
        return [input_item]
    # Numpy arrays are processed based on their dimensionality. This has to do with the fact that zero-dimensional
    # numpy arrays are interpreted as scalars by some numpy methods and as arrays by others.
    if isinstance(input_item, np.ndarray):
        if input_item.ndim <= 1 and input_item.size == 1:
            # A single-element flat array is unwrapped via item() so that the list holds a Python scalar rather than
            # a numpy one. The dimensionality bound keeps the unwrap away from arrays whose nesting must survive.
            return [input_item.item()]
        output_list: list[Any] = input_item.tolist()
        return output_list
    if isinstance(input_item, list):
        return input_item
    if isinstance(input_item, Iterable):
        return list(input_item)
    message = (
        f"Unable to convert the input item to a Python list, as items of type {type(input_item).__name__} "
        f"are not supported."
    )
    console.error(message=message, error=TypeError)
    # Unreachable: console.error() is NoReturn, but ruff cannot trace NoReturn through method calls (RET503).
    raise TypeError(message)  # pragma: no cover


def chunk_iterable(
    iterable: NDArray[Any] | tuple[Any, ...] | list[Any], chunk_size: int
) -> Generator[tuple[Any, ...] | NDArray[Any], None, None]:
    """Yields successive chunks from the input ordered Python iterable or NumPy array.

    Notes:
        For NumPy arrays, the function maintains the original data type and dimensionality, returning NumPy array
        chunks. For other iterables, it always returns chunks as tuples.

        The last yielded chunk contains any leftover elements if the iterable's length is not evenly divisible by
        ``chunk_size``. This last chunk may be smaller than all other chunks.

    Args:
        iterable: The Python iterable or NumPy array to split into chunks.
        chunk_size: The maximum number of elements in each chunk.

    Yields:
        Chunks of the input iterable (as a tuple) or NumPy array, containing at most ``chunk_size`` elements.

    Raises:
        TypeError: If ``iterable`` is not of a correct type.
        ValueError: If ``chunk_size`` is below 1.
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

    # The chunking loop lives in a separate generator so that the validation above runs when this function is called
    # rather than when the returned generator is first advanced.
    return _generate_chunks(iterable=iterable, chunk_size=chunk_size)


def error_format(message: str) -> str:
    """Formats the input message to match the default Console format and escapes it for regular expression matching.

    Notes:
        The formatting parameters are read from the global console variable, so the output always matches the
        configuration used by the Console class.

    Args:
        message: The message to format.

    Returns:
        The formatted and escaped message.
    """
    return re.escape(console.format_message(message=message, loguru=False))


def resolve_worker_count(
    requested_workers: int = 0,
    reserved_cores: int = 2,
) -> int:
    """Determines the number of CPU cores to allocate for a processing job.

    A positive ``requested_workers`` is honored exactly, capped only by the logical core count, so an explicit
    request can claim every core on the machine. A non-positive ``requested_workers`` auto-resolves to every available
    core minus ``reserved_cores``, clamped to at least 1, leaving headroom for the host system. If the core count
    cannot be auto-detected, the budget falls back to 1. The reserved cores apply only when the worker count
    auto-resolves.

    Args:
        requested_workers: The number of workers to allocate. A positive value is honored up to the logical core
            count. Non-positive values auto-resolve to all available cores minus the reserved cores.
        reserved_cores: The number of cores to reserve for host-system use during auto-resolution. Ignored for a
            positive ``requested_workers``. Must be >= 0.

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

    available_cores = cpu_count()
    if available_cores is None:
        return 1

    # A positive request is honored exactly, capped only by the logical core count. The reserved cores apply solely
    # to auto-resolution, so an explicit request can claim every core, which is the intended behavior on a dedicated
    # compute node where every core serves the job.
    if requested_workers > 0:
        return min(requested_workers, available_cores)

    # A non-positive request auto-resolves to every core minus the reserved system cores, clamped to at least one.
    return max(1, available_cores - reserved_cores)


def resolve_parallel_job_capacity(workers_per_job: int) -> int:
    """Determines how many jobs can run in parallel given the per-job core allocation.

    Divides the available core count by ``workers_per_job``, returning at least 1. If the core count cannot be
    auto-detected, returns 1.

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

    available_cores = cpu_count()
    if available_cores is None:
        return 1

    return max(1, available_cores // workers_per_job)


def convert_scalar_to_bytes(
    value: int | float | bool | np.generic,  # noqa: PYI041, FBT001
    dtype: np.dtype[Any] = _DEFAULT_SCALAR_DTYPE,
) -> NDArray[np.uint8]:
    """Serializes a scalar value to a uint8 byte array.

    The returned array length depends on the dtype: 1 byte for uint8/int8/bool, 2 for int16/uint16, 4 for
    int32/uint32/float32, 8 for int64/uint64/float64, etc.

    Notes:
        Uses an internal LRU cache keyed on the ``(value, repr(value), dtype_str)`` tuple. The repr component
        separates entries that compare equal while serializing to different bytes, which covers 0.0 against -0.0 and
        every int, float, and bool that shares a numeric value. The cached raw bytes are converted to a new numpy
        array on each call, avoiding mutation issues. This benefits tight loops where the same value+dtype pair is
        serialized repeatedly.

    Args:
        value: The scalar value to serialize.
        dtype: The numpy dtype specifying the target type and byte order.

    Returns:
        A 1D numpy array of dtype uint8 containing the serialized bytes.

    Raises:
        ValueError: If ``value`` carries a fractional part that the target integer ``dtype`` is unable to represent.
    """
    # Converts numpy scalar types to Python scalars for cache key hashability.
    if isinstance(value, np.generic):
        value = value.item()

    # A cast from a fractional float to an integer dtype discards the fraction without raising, so the mismatch is
    # rejected here. Integral floats round trip exactly and are accepted, and booleans are integers in Python and so
    # never reach this branch.
    if isinstance(value, float) and not value.is_integer() and dtype.kind in "iu":
        message = (
            f"Invalid 'value' argument encountered when converting scalar to bytes. Expected a value the target "
            f"dtype is able to represent, but encountered {value}, whose fractional part the cast to {dtype} would "
            f"discard."
        )
        console.error(message=message, error=ValueError)

    # An lru_cache resolves keys by equality, and -0.0, 0.0, 0, and False all compare equal while -0.0 alone carries
    # the sign bit. Passing repr(value) alongside the value gives each of them its own entry.
    raw = _cached_convert_scalar_to_bytes(value=value, value_key=repr(value), dtype_str=dtype.str)
    return np.frombuffer(raw, dtype=np.uint8).copy()


def convert_bytes_to_scalar(
    data: NDArray[np.uint8],
    dtype: np.dtype[Any] = _DEFAULT_SCALAR_DTYPE,
) -> int | float | bool:
    """Deserializes a uint8 byte array to a Python scalar.

    Args:
        data: A 1D numpy array of dtype uint8 containing the serialized bytes.
        dtype: The numpy dtype specifying the target type and byte order.

    Returns:
        The deserialized Python int, float, or bool value.

    Raises:
        TypeError: If ``data`` is not a uint8 numpy array.
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

    # np.frombuffer rejects a strided array, so a non-contiguous input is compacted before it is reinterpreted.
    result: int | float | bool = dtype.type(np.frombuffer(np.ascontiguousarray(data), dtype=dtype)[0]).item()
    return result


def convert_array_to_bytes(array: NDArray[Any]) -> NDArray[np.uint8]:
    """Serializes a 1D numpy array of any supported dtype to a uint8 byte array.

    The returned array owns its memory, so mutating it leaves the source array unchanged.

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

    # np.frombuffer rejects a strided array, so a non-contiguous input is compacted before it is reinterpreted.
    return np.frombuffer(np.ascontiguousarray(array), dtype=np.uint8).copy()


def convert_bytes_to_array(
    data: NDArray[np.uint8],
    dtype: np.dtype[Any],
) -> NDArray[Any]:
    """Deserializes a uint8 byte array to a typed numpy array.

    Args:
        data: A 1D numpy array of dtype uint8 containing the serialized bytes.
        dtype: The numpy dtype specifying the target element type and byte order.

    Returns:
        A 1D numpy array of the specified dtype containing the deserialized values.

    Raises:
        TypeError: If ``data`` is not a uint8 numpy array.
        ValueError: If ``data`` is not 1D or its byte count is not evenly divisible by the target dtype's itemsize.
    """
    if not isinstance(data, np.ndarray) or data.dtype != np.uint8:
        message = (
            f"Invalid 'data' type encountered when converting bytes to array. Expected a uint8 numpy array, but "
            f"encountered {type(data).__name__} with dtype {getattr(data, 'dtype', 'N/A')}."
        )
        console.error(message=message, error=TypeError)

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

    # np.frombuffer rejects a strided array, so a non-contiguous input is compacted before it is reinterpreted.
    return np.frombuffer(np.ascontiguousarray(data), dtype=dtype).copy()


def _generate_chunks(
    iterable: NDArray[Any] | tuple[Any, ...] | list[Any], chunk_size: int
) -> Generator[tuple[Any, ...] | NDArray[Any], None, None]:
    """Yields successive chunks from an iterable that chunk_iterable() has already validated.

    Args:
        iterable: The Python iterable or NumPy array to split into chunks.
        chunk_size: The maximum number of elements in each chunk.

    Yields:
        Chunks of the input iterable (as a tuple) or NumPy array, containing at most ``chunk_size`` elements.
    """
    # Chunking is performed along the first dimension for both NumPy arrays and Python iterable sequences.
    # This preserves array dimensionality within chunks for NumPy arrays.
    chunks_are_arrays = isinstance(iterable, np.ndarray)
    for start_index in range(0, len(iterable), chunk_size):
        chunk_slice = iterable[start_index : start_index + chunk_size]
        yield np.array(chunk_slice) if chunks_are_arrays else tuple(chunk_slice)


@lru_cache(maxsize=4096)
def _cached_convert_scalar_to_bytes(
    value: int | float | bool,  # noqa: PYI041, FBT001
    value_key: str,  # noqa: ARG001
    dtype_str: str,
) -> bytes:
    """Serializes a scalar value to raw bytes using an LRU cache.

    Args:
        value: The scalar value to serialize.
        value_key: The repr() of the value, which separates cache entries whose values compare equal while
            serializing to different bytes. The body never reads it, since its only role is to widen the key the
            lru_cache decorator builds from the argument list.
        dtype_str: The numpy dtype string specifying the target type and byte order.

    Returns:
        The raw bytes representing the serialized scalar.
    """
    return np.array([value], dtype=dtype_str).view(dtype=np.uint8).tobytes()
