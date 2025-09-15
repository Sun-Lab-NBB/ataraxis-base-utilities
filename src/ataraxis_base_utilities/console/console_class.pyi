from enum import StrEnum
from pathlib import Path
from collections.abc import Callable as Callable

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

class Console:
    _line_width: int
    _break_long_words: bool
    _break_on_hyphens: bool
    _debug_log_path: Path | None
    _message_log_path: Path | None
    _error_log_path: Path | None
    _is_enabled: bool
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
    ) -> None: ...
    def __repr__(self) -> str: ...
    def _add_handles(self, *, debug: bool = False, enqueue: bool = False) -> None: ...
    def enable(self) -> None: ...
    def disable(self) -> None: ...
    @property
    def debug_log_path(self) -> Path | None: ...
    @property
    def message_log_path(self) -> Path | None: ...
    @property
    def error_log_path(self) -> Path | None: ...
    @property
    def enabled(self) -> bool: ...
    def format_message(self, message: str, *, loguru: bool = False) -> str: ...
    def echo(self, message: str, level: str | LogLevel = ...) -> None: ...
    def error(self, message: str, error: Callable[..., Exception] = ...) -> None: ...

console: Console
