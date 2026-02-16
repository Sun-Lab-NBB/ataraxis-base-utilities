"""Contains tests for functions provided by the standalone_methods package."""

from typing import Any

import numpy as np
import pytest

from ataraxis_base_utilities import ensure_list, error_format, chunk_iterable


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
        list(chunk_iterable(iterable=1, chunk_size=2))

    message = (
        f"Unsupported 'chunk_size' value encountered when chunking iterable. Expected a positive non-zero value, "
        f"but encountered {-4}."
    )
    with pytest.raises(ValueError, match=error_format(message=message)):
        list(chunk_iterable(iterable=[1, 2, 3], chunk_size=-4))
