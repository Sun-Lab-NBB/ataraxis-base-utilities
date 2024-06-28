from _typeshed import Incomplete
from collections.abc import Callable as Callable
from enum import Enum
from functools import wraps as wraps
from loguru._logger import Logger as Logger
from os import PathLike as PathLike
from pathlib import Path
from typing import Any, Literal

class LogLevel(Enum):
    """Maps valid literal arguments that can be passed to some Console class methods to programmatically callable
    variables.

    Use this enumeration instead of 'hardcoding' logging levels where possible to automatically adjust to future API
    changes of this library.
    """
    DEBUG: str
    INFO: str
    SUCCESS: str
    WARNING: str
    ERROR: str
    CRITICAL: str

class LogBackends(Enum):
    """Maps valid backend options that can be used to instantiate the Console class to programmatically addressable
    variables.

    Use this enumeration to specify the backend used by the Console class to display and save logged messages to files.
    """
    LOGURU: str
    CLICK: str

class Console:
    """Provides methods for configuring and using loguru-based pipelines that generate, display and log information
    and error messages.

    This class functions as a centralized API used by all project Ataraxis modules that abstracts module-console
    interactions. The use of a dedicated class (and library) to control messaging functionality allows any Ataraxis
    module to naturally integrate with the rest of the project. Additionally, decoupling message pipeline
    implementation from module's source code allows more flexibility when developing our messaging standards and APIs.

    Args:
        logger_backend: Specifies the backend used to manage terminal and file logs. Valid values are available through
            LogBackends enumeration and are currently limited to LOGURU and CLICK. Defaults to LOGURU.
        line_width: The maximum number of characters in a single line of displayed text. This is primarily used to
            limit the width of the text block as it is displayed in the terminal and saved to log files. Defaults to
            120.
        message_log_path: The path to the file used to log non-error messages (info to warning levels). If not provided
            (set to None), logging non-error messages will be disabled. Defaults to None.
        error_log_path: The path to the file used to log error messages (error and critical levels). If not provided
            (set to None), logging non-error messages will be disabled. Defaults to None.
        debug_log_path: The path to the file used to log debug messages (detail levels vary). If not provided
            (set to None), logging non-error messages will be disabled. Defaults to None.
        break_long_words: Determines whether long words can be broken-up when then text block is
            formatted to fit the width requirement. Defaults to False.
        break_on_hyphens: determines whether breaking sentences on hyphens is allowed when text
            block is formatted to fit the width requirement. Defaults to False.
        use_color: Determines whether terminal output should be colorized. Defaults to True.

    Attributes:
        _line_width: Stores the maximum allowed text block width, in characters.
        _break_long_words: Determines whether to break text on long words.
        _break_on_hyphens: Determines whether to break text on hyphens.
        _use_color: Determines whether to colorize terminal output.
        _message_log_path: Stores the path to the message log file.
        _error_log_path: Stores the path to the error log file.
        _debug_log_path: Stores the path to the debug log file.
        _backend: Tracks logger backends used by the console class.
        _logger: When logging backend is set to LOGURU, stores the instance of the loguru 'Logger' class used to manage
            the logs. Otherwise, it is to None.
        _is_enabled: Tracks whether logging through this class instance is enabled or disabled. Initializes to False.

    Raises:
        ValueError: If any of the provided file paths is not valid.
        ValidationError: If any of the input arguments are not of a valid type.
    """
    _line_width: Incomplete
    _break_long_words: Incomplete
    _break_on_hyphens: Incomplete
    _use_color: Incomplete
    _debug_log_path: Incomplete
    _message_log_path: Incomplete
    _error_log_path: Incomplete
    _backend: Incomplete
    _logger: Incomplete
    _is_enabled: bool
    def __init__(self, logger_backend: Literal[LogBackends.LOGURU, LogBackends.CLICK] = ..., message_log_path: Path | str | None = None, error_log_path: Path | str | None = None, debug_log_path: Path | str | None = None, line_width: int = 120, break_long_words: bool = False, break_on_hyphens: bool = False, use_color: bool = True) -> None: ...
    def add_handles(self, *, remove_existing_handles: bool = True, debug_terminal: bool = False, debug_file: bool = False, message_terminal: bool = True, message_file: bool = False, error_terminal: bool = True, error_file: bool = False, enqueue: bool = False) -> None:
        """Reconfigures the local loguru Logger class instance to use default project Ataraxis handles.

        This enforces the necessary formatting and, overall, is a prerequisite to use the loguru backend to
        display messages. This method only needs to be called once, preferably from the top of the call hierarchy, for
        interactive libraries. Do not call this method from API runtimes to avoid interfering with upstream processes
        instantiating their own handles.

        Notes:
            The method can be flexibly configured to only add a subset of all supported handles. For example,
            by default, it does not add debug handles, making it impossible to display or log debug messages. It can
            also be configured to not remove existing handles (default behavior) if necessary. See argument docstrings
            below for more information.

            During runtime, handles determine what happens to the message passed via appropriate 'log' call. Loguru
            shares the set of handles across all 'logger' instances, which means this method should be used with
            caution, as it can interfere with any other handles, including the default ones.

        Args:
            remove_existing_handles: Determines whether to remove all existing handles before adding new loguru handles.
                Defaults to True.
            debug_terminal: Determines whether to add the handle that prints debug-level messages to terminal.
            debug_file: Determines whether to add the handle that writes debug-level messages to log file.
            message_terminal: Same as debug_terminal, but for information, success and warning level messages.
            message_file: Same as debug_file, but for information, success and warning level messages.
            error_terminal: Same as debug_terminal, but for error and critical level messages.
            error_file: Same as debug_file, but for error and critical level messages.
            enqueue: Determines if messages are processed synchronously or asynchronously. Generally, this option is
                only suggested for multiprocessing runtimes that log data from multiple processes, as queueing messages
                prevents race conditions and other unsafe operations.

        Raises:
            ValidationError: If any of the input arguments are not of a valid type.
        """
    def enable(self) -> None:
        """A switch that enables logging messages and errors with this Console class."""
    def disable(self) -> None:
        """A switch that disables logging messages and errors with this Console class."""
    @property
    def has_handles(self) -> bool:
        """Returns True if the class uses LOGURU backend and the backend has configured handles.

        If the class does not use loguru backend or if the class uses loguru and does nt have handles, returns False."""
    @property
    def is_enabled(self) -> bool:
        """Returns True if logging with this Console class instance is enabled."""
    @staticmethod
    def _ensure_directory_exists(path: Path) -> None:
        """Determines if the directory portion of the input path exists and, if not, creates it.

        When the input path ends with an .extension (indicating this a file path), the file portion is ignored and
        only the directory path is evaluated.

        Args:
            path: The string-path to be processed. Should use os-defined delimiters, as os.path.splitext() is used to
                decompose the path into nodes.
        """
    def format_message(self, message: str, *, loguru: bool = False) -> str:
        """Formats the input message string according to the standards used across Ataraxis and related projects.

        Args:
            message: The text string to format to display according to Ataraxis standards.
            loguru: A flag that determines if the message is intended to be processed via loguru backend or
                another method or backend (e.g.: Exception class or click backend). Defaults to False.

        Returns:
            Formatted text message (augmented with newline and other service characters as necessary).

        Raises:
            ValidationError: If the 'message' argument is not a string.
        """
    def echo(self, message: str, level: LogLevel = ..., *, terminal: bool = True, log: bool = False) -> bool:
        """Formats the input message according to the class configuration and outputs it to the terminal, file or both.

        In a way, this can be seen as a better 'print'. It does a lot more than just print though, especially when the
        Console class uses loguru backend.

        Args:
            message: The text to be printed to terminal, written to log file, or both.
            level: Only for loguru backends. The level to log the message at. This method supports all levels available
                through the LogLevel enumeration, but is primarily intended to be used for infor, success and warning
                messages.
            terminal: The flag that determines whether the message should be printed to the terminal using the class
                logging backend. Defaults to True.
            log: The flag that determines whether the message should be written to a file using the class logging
                backend. Note, if valid message_log_path or debug_log_path were not provided, this flag will be
                meaningless, as there will be no handle to write ot file. Defaults to False.

        Returns:
            True if the message has been processed and False if the message cannot be printed because the Console is
                disabled.

        Raises:
            ValidationError: If any of the input arguments are not of a valid type.
            RuntimeError: If the method is called while using loguru backend without any active logger handles.
        """
    def error(self, message: str, error: Callable[..., Exception] = ..., callback: Callable[[], Any] | None = None, *, terminal: bool = True, log: bool = False, reraise: bool = True) -> None:
        """Raises and immediately logs the requested error.

        This method allows to flexibly raise errors, while customizing (to a degree) the way errors are logged. Note,
        if the parent class instance is disabled, the method will return without processing the error.

        Args:
            message: The error-message to pass to the error callable.
            error: The callable Exception class to be raised by the method. Defaults to RuntimeError.
            callback: Optional, only for loguru logging backends. The function to call after catching the exception.
                This can be used to terminate or otherwise alter the runtime without relying on the standard python
                mechanism of retracing the call stack. For example, sys.exit(1) can be passed as a callable to
                terminate early. Defaults to None.
            terminal: The flag that determines whether the error should be printed to the terminal using the class
                logging backend. Defaults to True.
            log: The flag that determines whether the error should be written to a file using the class logging backend.
                Note, if valid error_log_path was not provided, this flag will be meaningless, as there will be no
                handle to write ot file. Defaults to False.
            reraise: The flag that determines whether the error is to be reraised after being caught and handled by
                loguru backend. For non-loguru backends, this determines if the error is raised in the first place or
                if the method only logs the error message. Defaults to True.

        Raises:
            ValidationError: If any of the inputs are not of a valid type.
            RuntimeError: If the method is called while using loguru backend without any active logger handles.
        """
