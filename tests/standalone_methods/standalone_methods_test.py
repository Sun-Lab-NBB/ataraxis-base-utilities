"""Contains tests for functions provided by the standalone_methods package."""

from typing import Any
from unittest.mock import patch

import numpy as np
import pytest

from ataraxis_base_utilities import (
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


# noinspection PyRedundantParentheses
@pytest.mark.parametrize(
    "input_item, expected",
    [
        ([1, 2, 3], [1, 2, 3]),
        ((1, 2, 3), [1, 2, 3]),
        ({1, 2, 3}, [1, 2, 3]),
        ([1], [1]),
        ((1), [1]),
        ({1}, [1]),
        (np.array([1, 2, 3]), [1, 2, 3]),
        (np.array([[1, 2, 3], [4, 5, 6]]), [[1, 2, 3], [4, 5, 6]]),
        (np.array([1]), [1]),
        (1, [1]),
        (1.0, [1.0]),
        ("a", ["a"]),
        (True, [True]),
        (None, [None]),
        (np.int32(1), [1]),
    ],
)
def test_ensure_list(input_item: Any, expected: list[Any]) -> None:
    """Verifies the functioning of the ensure_list() function for all supported input scenarios."""
    output = ensure_list(input_item=input_item)
    # Checks output value
    assert output == expected
    # Checks output type
    assert type(output) is type(expected)


def test_ensure_list_error() -> None:
    """Verifies that ensure_list() correctly handles unsupported input types."""
    message = (
        f"Unable to convert the input item to a Python list, as items of type {type(object()).__name__} are not "
        f"supported."
    )
    # noinspection PyTypeChecker
    with pytest.raises(TypeError, match=error_format(message=message)):
        ensure_list(input_item=object())


# noinspection PyRedundantParentheses
@pytest.mark.parametrize(
    "input_iterable, chunk_size, expected_chunks",
    [
        ([1, 2, 3, 4, 5], 2, [(1, 2), (3, 4), (5,)]),
        (np.array([1, 2, 3, 4, 5]), 2, [np.array([1, 2]), np.array([3, 4]), np.array([5])]),
        ((1, 2, 3, 4, 5), 3, [(1, 2, 3), (4, 5)]),
    ],
)
def test_chunk_iterable(input_iterable: Any, chunk_size: int, expected_chunks: Any) -> None:
    """Verifies the functioning of the chunk_iterable() function for various input types and chunk sizes."""
    # Returns a generator that can be iterated to get successive chunks
    result = list(chunk_iterable(iterable=input_iterable, chunk_size=chunk_size))

    # Verifies that the obtained number of chunks matches expectation
    assert len(result) == len(expected_chunks)

    # Verifies that the individual chunks match expected chunks
    for result_chunk, expected_chunk in zip(result, expected_chunks):
        if isinstance(result_chunk, np.ndarray):
            assert np.array_equal(result_chunk, expected_chunk)
        else:
            assert result_chunk == expected_chunk


def test_chunk_iterable_error() -> None:
    """Verifies that chunk_iterable() correctly handles unsupported iterable types and chunk_size values."""
    message: str = (
        f"Unsupported 'iterable' type encountered when chunking iterable. Expected a list, tuple or numpy array, "
        f"but encountered {1} of type {type(1).__name__}."
    )
    with pytest.raises(TypeError, match=error_format(message=message)):
        # noinspection PyTypeChecker
        list(chunk_iterable(iterable=1, chunk_size=2))

    message = (
        f"Unsupported 'chunk_size' value encountered when chunking iterable. Expected a positive non-zero value, "
        f"but encountered {-4}."
    )
    with pytest.raises(ValueError, match=error_format(message=message)):
        list(chunk_iterable(iterable=[1, 2, 3], chunk_size=-4))


@pytest.mark.parametrize(
    "requested, reserved, mock_cpu, expected",
    [
        # Explicit request within budget: 8 requested, budget = 16 - 2 = 14, returns 8.
        (8, 2, 16, 8),
        # Explicit request exceeding budget: 50 requested, budget = 16 - 2 = 14, clamped to 14.
        (50, 2, 16, 14),
        # Zero requests all available: budget = 16 - 2 = 14.
        (0, 2, 16, 14),
        # Negative requests all available (same as zero): budget = 16 - 2 = 14.
        (-1, 2, 16, 14),
        # Budget clamps to 1 when available equals reserved.
        (0, 4, 4, 1),
        # Zero reserved cores: full core count returned.
        (0, 0, 8, 8),
        # cpu_count returns None, falls back to reserved_cores. max(1, reserved - reserved) = 1.
        (0, 2, None, 1),
        # Explicit request of 1 on a large machine: returns 1.
        (1, 2, 16, 1),
    ],
)
def test_resolve_worker_count(requested: int, reserved: int, mock_cpu: int | None, expected: int) -> None:
    """Verifies resolve_worker_count() for capped requests, auto-detection, and None cpu_count fallback."""
    with patch("ataraxis_base_utilities.standalone_methods.standalone_methods.cpu_count", return_value=mock_cpu):
        result = resolve_worker_count(requested_workers=requested, reserved_cores=reserved)
    assert result == expected


def test_resolve_worker_count_error() -> None:
    """Verifies resolve_worker_count() raises errors for negative reserved_cores."""
    with pytest.raises(ValueError, match="Invalid 'reserved_cores' value"):
        resolve_worker_count(reserved_cores=-1)


# --- resolve_parallel_job_capacity tests ---


@pytest.mark.parametrize(
    "workers_per_job, mock_cpu, expected",
    [
        (4, 16, 4),
        (8, 16, 2),
        (1, 8, 8),
        (16, 16, 1),
        (32, 16, 1),
        # cpu_count returns None: always 1.
        (4, None, 1),
    ],
)
def test_resolve_parallel_job_capacity(workers_per_job: int, mock_cpu: int | None, expected: int) -> None:
    """Verifies resolve_parallel_job_capacity() for various core counts and None fallback."""
    with patch("ataraxis_base_utilities.standalone_methods.standalone_methods.cpu_count", return_value=mock_cpu):
        result = resolve_parallel_job_capacity(workers_per_job=workers_per_job)
    assert result == expected


@pytest.mark.parametrize("workers_per_job", [0, -1, -10])
def test_resolve_parallel_job_capacity_error(workers_per_job: int) -> None:
    """Verifies resolve_parallel_job_capacity() raises errors for invalid workers_per_job."""
    with pytest.raises(ValueError, match="Invalid 'workers_per_job' value"):
        resolve_parallel_job_capacity(workers_per_job=workers_per_job)


# --- convert_scalar_to_bytes tests ---


@pytest.mark.parametrize(
    "value, dtype, expected_nbytes",
    [
        (42, np.dtype("<i8"), 8),
        (0, np.dtype("<i8"), 8),
        (-1, np.dtype("<i4"), 4),
        (255, np.dtype("uint8"), 1),
        (1000, np.dtype("<u4"), 4),
        (3.14, np.dtype("<f8"), 8),
        (-2.5, np.dtype("<f4"), 4),
        (1, np.dtype(">i2"), 2),
        (True, np.dtype("bool"), 1),
        (0, np.dtype("uint8"), 1),
        (np.int32(42), np.dtype("<i4"), 4),
        (np.float64(3.14), np.dtype("<f8"), 8),
    ],
)
def test_convert_scalar_to_bytes(value: Any, dtype: np.dtype[Any], expected_nbytes: int) -> None:
    """Verifies convert_scalar_to_bytes() produces correct shape, dtype, and byte count for various dtypes."""
    result = convert_scalar_to_bytes(value=value, dtype=dtype)
    assert result.dtype == np.uint8
    assert result.ndim == 1
    assert result.nbytes == expected_nbytes

    # Roundtrip verification: deserialize and compare.
    roundtrip = convert_bytes_to_scalar(data=result, dtype=dtype)
    expected_val = dtype.type(value).item()
    assert roundtrip == pytest.approx(expected_val)


def test_convert_scalar_to_bytes_cache() -> None:
    """Verifies that the LRU cache returns correct values and different inputs produce different results."""
    dtype = np.dtype("<i4")

    # Same value+dtype should return equivalent arrays.
    a = convert_scalar_to_bytes(value=42, dtype=dtype)
    b = convert_scalar_to_bytes(value=42, dtype=dtype)
    assert np.array_equal(a, b)

    # Different values should produce different byte arrays.
    c = convert_scalar_to_bytes(value=43, dtype=dtype)
    assert not np.array_equal(a, c)

    # Mutating one result should not affect subsequent calls (copy safety).
    a[0] = 0
    d = convert_scalar_to_bytes(value=42, dtype=dtype)
    assert np.array_equal(b, d)


# --- convert_bytes_to_scalar tests ---


@pytest.mark.parametrize(
    "value, dtype",
    [
        (42, np.dtype("<i8")),
        (-1, np.dtype("<i4")),
        (255, np.dtype("uint8")),
        (1000, np.dtype("<u4")),
        (3.14, np.dtype("<f8")),
        (-2.5, np.dtype("<f4")),
        (1, np.dtype(">i2")),
        (True, np.dtype("bool")),
        (0, np.dtype("<i8")),
        (2**63 - 1, np.dtype("<i8")),
        (2**32 - 1, np.dtype("<u4")),
    ],
)
def test_convert_bytes_to_scalar(value: Any, dtype: np.dtype[Any]) -> None:
    """Verifies roundtrip scalar serialization/deserialization across all supported dtypes."""
    serialized = convert_scalar_to_bytes(value=value, dtype=dtype)
    result = convert_bytes_to_scalar(data=serialized, dtype=dtype)
    expected = dtype.type(value).item()
    assert result == pytest.approx(expected)
    assert isinstance(result, (int, float))


def test_convert_bytes_to_scalar_error() -> None:
    """Verifies convert_bytes_to_scalar() raises errors for invalid inputs."""
    # Wrong size: 4 bytes for an 8-byte dtype.
    wrong_size = np.array([1, 2, 3, 4], dtype=np.uint8)
    with pytest.raises(ValueError, match="Invalid 'data' size"):
        convert_bytes_to_scalar(data=wrong_size, dtype=np.dtype("<i8"))

    # Wrong ndim: 2D array.
    wrong_ndim = np.array([[1, 2], [3, 4]], dtype=np.uint8)
    with pytest.raises(ValueError, match="Invalid 'data' shape"):
        convert_bytes_to_scalar(data=wrong_ndim, dtype=np.dtype("<i4"))

    # Wrong dtype: not uint8.
    wrong_dtype = np.array([1, 2, 3, 4], dtype=np.int32)
    with pytest.raises(TypeError, match="Invalid 'data' type"):
        # noinspection PyTypeChecker
        convert_bytes_to_scalar(data=wrong_dtype, dtype=np.dtype("<i4"))


# --- convert_array_to_bytes tests ---


@pytest.mark.parametrize(
    "array",
    [
        np.array([1, 2, 3, 4], dtype=np.int32),
        np.array([1.5, 2.5, 3.5], dtype=np.float64),
        np.array([True, False, True], dtype=np.bool_),
        np.array([0, 255], dtype=np.uint8),
        np.array([1, 2, 3], dtype=np.int64),
        np.array([1, 2], dtype=np.float32),
    ],
)
def test_convert_array_to_bytes(array: Any) -> None:
    """Verifies convert_array_to_bytes() produces correct uint8 arrays and round-trips correctly."""
    result = convert_array_to_bytes(array=array)
    assert result.dtype == np.uint8
    assert result.ndim == 1
    assert result.nbytes == array.nbytes

    # Roundtrip verification.
    roundtrip = convert_bytes_to_array(data=result, dtype=array.dtype)
    assert np.array_equal(roundtrip, array)


def test_convert_array_to_bytes_error() -> None:
    """Verifies convert_array_to_bytes() raises errors for multidimensional and empty arrays."""
    # Multidimensional array.
    multi_dim = np.array([[1, 2], [3, 4]], dtype=np.int32)
    with pytest.raises(ValueError, match="Invalid 'array' shape"):
        convert_array_to_bytes(array=multi_dim)

    # Empty array.
    empty = np.array([], dtype=np.int32)
    with pytest.raises(ValueError, match="Invalid 'array' size"):
        convert_array_to_bytes(array=empty)


# --- convert_bytes_to_array tests ---


@pytest.mark.parametrize(
    "array",
    [
        np.array([10, 20, 30], dtype=np.int32),
        np.array([1.0, 2.0], dtype=np.float64),
        np.array([True, False, True, False], dtype=np.bool_),
        np.array([100, 200], dtype=np.uint16),
    ],
)
def test_convert_bytes_to_array(array: Any) -> None:
    """Verifies roundtrip array serialization/deserialization."""
    serialized = convert_array_to_bytes(array=array)
    result = convert_bytes_to_array(data=serialized, dtype=array.dtype)
    assert np.array_equal(result, array)
    assert result.dtype == array.dtype


def test_convert_bytes_to_array_error() -> None:
    """Verifies convert_bytes_to_array() raises errors for invalid inputs."""
    # Byte count not divisible by dtype itemsize (3 bytes for int32 = 4 bytes).
    bad_size = np.array([1, 2, 3], dtype=np.uint8)
    with pytest.raises(ValueError, match="Invalid 'data' size"):
        convert_bytes_to_array(data=bad_size, dtype=np.dtype("<i4"))

    # Wrong ndim: 2D array.
    wrong_ndim = np.array([[1, 2], [3, 4]], dtype=np.uint8)
    with pytest.raises(ValueError, match="Invalid 'data' shape"):
        convert_bytes_to_array(data=wrong_ndim, dtype=np.dtype("<i4"))
