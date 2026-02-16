from enum import StrEnum
from typing import NoReturn
from pathlib import Path
from contextlib import contextmanager
from collections.abc import (
    Callable as Callable,
    Iterable,
    Iterator,
)

from tqdm import tqdm

class LogLevel(StrEnum):
    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class LogFormats(StrEnum):
    LOG = ".log"
    TXT = ".txt"
    JSON = ".json"

def ensure_directory_exists(path: Path) -> None: ...

class ProgressBar:
    _tqdm_bar: tqdm[NoReturn]
    def __init__(self, tqdm_bar: tqdm[NoReturn]) -> None: ...
    def __repr__(self) -> str: ...
    def update(self, n: float = 1) -> None: ...
    def close(self) -> None: ...

class Console:
    _line_width: int
    _break_long_words: bool
    _break_on_hyphens: bool
    _debug_log_path: Path | None
    _message_log_path: Path | None
    _error_log_path: Path | None
    _is_enabled: bool
    _show_progress: bool
    def __init__(
        self,
        log_directory: Path | None = None,
        log_format: str | LogFormats = ...,
        line_width: int = 120,
        *,
        break_long_words: bool = False,
        break_on_hyphens: bool = False,
        debug: bool = False,
        enqueue: bool = False,
        show_progress: bool = False,
    ) -> None: ...
    def __repr__(self) -> str: ...
    def enable(self) -> None: ...
    def disable(self) -> None: ...
    @contextmanager
    def temporarily_enabled(self) -> Iterator[None]: ...
    def enable_progress(self) -> None: ...
    def disable_progress(self) -> None: ...
    @property
    def debug_log_path(self) -> Path | None: ...
    @property
    def message_log_path(self) -> Path | None: ...
    @property
    def error_log_path(self) -> Path | None: ...
    @property
    def enabled(self) -> bool: ...
    @property
    def progress_enabled(self) -> bool: ...
    def format_message(self, message: str, *, loguru: bool = False) -> str: ...
    def echo(self, message: str, level: str | LogLevel = ..., *, raw: bool = False) -> None: ...
    def track[T](
        self, iterable: Iterable[T], description: str = "", total: float | None = None, unit: str = "iteration"
    ) -> Iterable[T]: ...
    @contextmanager
    def progress(self, total: float, description: str = "", unit: str = "iteration") -> Iterator[ProgressBar]: ...
    def error(self, message: str, error: Callable[..., Exception] = ...) -> NoReturn: ...
    def _add_handles(self, *, debug: bool = False, enqueue: bool = False) -> None: ...

console: Console
