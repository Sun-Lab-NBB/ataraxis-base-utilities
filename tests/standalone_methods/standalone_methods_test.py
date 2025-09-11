"""Contains tests for functions stored in the standalone_methods package."""

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
def test_ensure_list(input_item: Any, expected: list) -> None:
    """Verifies the functioning of the ensure_list() method for all supported scenarios.

    Tests the following inputs:
        - 0 multi-item lists
        - 1 multi-item tuples
        - 2 multi-item sets
        - 3 one-item lists
        - 4 one-item tuples
        - 5 one-item sets
        - 6 one-dimensional numpy arrays
        - 7 multidimensional numpy arrays
        - 9 zero-dimensional numpy arrays
        - 7 ints
        - 8 floats
        - 9 strings
        - 10 bools
        - 11 Nones
        - 12 Numpy scalars
    """
    output = ensure_list(input_item)
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
    with pytest.raises(TypeError, match=error_format(message)):
        # noinspection PyTypeChecker
        ensure_list(object())


# noinspection PyRedundantParentheses
@pytest.mark.parametrize(
    "input_iterable, chunk_size, expected_chunks",
    [
        ([1, 2, 3, 4, 5], 2, [(1, 2), (3, 4), (5,)]),
        (np.array([1, 2, 3, 4, 5]), 2, [np.array([1, 2]), np.array([3, 4]), np.array([5])]),
        ((1, 2, 3, 4, 5), 3, [(1, 2, 3), (4, 5)]),
    ],
)
def test_chunk_iterable(input_iterable, chunk_size: int, expected_chunks) -> None:
    """Verifies the functioning of the chunk_iterable() method for various input types and chunk sizes.

    Tests the following scenarios:
        - 0 List input with even chunks and a remainder
        - 1 NumPy array input with even chunks and a remainder
        - 2 Tuple input with uneven chunks
    """
    # Returns a generator that can be iterated to get successive chunks
    result = list(chunk_iterable(input_iterable, chunk_size))

    # Verifies that the obtained number of chunks matches expectation
    assert len(result) == len(expected_chunks)

    # Verifies that the individual chunks match expected chunks
    for r, e in zip(result, expected_chunks):
        if isinstance(r, np.ndarray):
            assert np.array_equal(r, e)
        else:
            assert r == e


def test_chunk_iterable_error() -> None:
    """Verifies that chunk_iterable() correctly handles unsupported iterables types and chunk_size values."""
    message: str = (
        f"Unsupported 'iterable' type encountered when chunking iterable. Expected a list, tuple or numpy array, "
        f"but encountered {1} of type {type(1).__name__}."
    )
    with pytest.raises(TypeError, match=error_format(message)):
        list(chunk_iterable(iterable=1, chunk_size=2))

    message = (
        f"Unsupported 'chunk_size' value encountered when chunking iterable. Expected a positive non-zero value, "
        f"but encountered {-4}."
    )
    with pytest.raises(ValueError, match=error_format(message)):
        list(chunk_iterable(iterable=[1, 2, 3], chunk_size=-4))
