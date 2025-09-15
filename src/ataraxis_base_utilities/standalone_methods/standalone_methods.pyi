from typing import Any
from collections.abc import Generator

from numpy.typing import NDArray as NDArray

from ..console import console as console

def ensure_list(input_item: Any) -> list[Any]: ...
def chunk_iterable(
    iterable: NDArray[Any] | tuple[Any] | list[Any], chunk_size: int
) -> Generator[tuple[Any, ...] | NDArray[Any], None, None]: ...
def error_format(message: str) -> str: ...
