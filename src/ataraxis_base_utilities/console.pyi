from _typeshed import Incomplete
from collections.abc import Callable as Callable
from dataclasses import dataclass
from enum import Enum
from loguru._logger import Logger as Logger
from pathlib import Path
from typing import Any, Literal

def default_callback(__error: str | int | None = None, /) -> Any:
    """Calls sys.exit() with a minimal explanation code.

    This is a wrapper over sys.exit() that can be used as the input to 'onerror' argument of loguru catch() method.
    The main advantage of using this callback over the plain sys.exit is that it avoids reprinting the exception
    message, reducing the output clutter.
    """

class LogLevel(Enum):
    """Maps valid literal arguments that can be passed to some Console class methods to programmatically callable
    variables.

    Use this enumeration instead of 'hardcoding' logging levels where possible to automatically adjust to future API
    changes of this library.

    Log level determines the 'severity' of the logged messages. In turn, this is used to conditionally filter incoming
    messages, depending on the configuration of the Console class loguru backend. For example, the end-user can disable
    the handles for 'DEBUG' level messages and suppress any message at or below DEBUG level.
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

    The backend determines the message and error processing engine used by the Console class. For most projects, it
    is highly advised to use the default loguru backend as it provides a more robust feature set, compared to
    'click' backend.
    """
    LOGURU: str
    CLICK: str

@dataclass
class LogExtensions:
    '''Maps valid file-extension options that can be used by log file paths provided to the Console class to
    programmatically addressable variables.

    Use this class to add valid extensions to the log-file paths used as input arguments when initializing new
    Console class instances or augmenting existing Console class instances via setter methods.

    File extensions are used to determine the log file format. Extensions exposed through this class already contain
    the \'.\' prefix and should be appended to plain file names. For example, to add .log extension, you can use:
    f"file_name{LogExtensions.LOG}"
    '''
    LOG: str = ...
    TXT: str = ...
    JSON: str = ...
    @classmethod
    def values(cls) -> tuple[str, ...]:
        """Returns the valid extension options packaged into a tuple.

        The returned tuple is used by the Console class to validate incoming log paths.
        """
    def __init__(self, LOG=..., TXT=..., JSON=...) -> None: ...

class Console:
    """After initial configuration, provides methods for terminal-printing and file-logging messages and errors.

    This class wraps multiple message-processing (logging and / or printing) backends and provides an API that allows
    configuring and using the wrapped backend in a consistent fashion across many projects. Overall, it is designed to
    largely behave like the standard 'print()' and 'raise' methods offered by the default Python library.

    Notes:
        Since this class is explicitly designed to be shared by multiple projects that may also be mutually-dependent,
        it defaults to a disabled state. When Console is initialized, calling its echo() (analogous to print()) method
        will not produce any output and calling error() (analogous to raise) method will behave like a standard
        'raise' method. To enable the full class functionality, the Console has to be configured (via add_handles() and
        enabled (via enable()) methods.

        Do not configure or enable the Console class from libraries that may be imported by other projects! To work
        properly, the Console has to be enabled at the highest level of the call hierarchy: from the main runtime
        script. Leave console configuration and enabling to the end-user.

    Args:
        logger_backend: Specifies the backend used to process message and error terminal-printing and file-logging.
            Valid backend options are available through LogBackends enumeration and are currently limited to
            LOGURU and CLICK.
        line_width: The maximum length, in characters, for a single line of displayed text. This is used to limit the
            width of the text block as it is displayed in the terminal and written to log files.
        debug_log_path: The path to the file used to log debug messages (messages at or below DEBUG level). If not
            provided (set to None), logging debug messages will be disabled.
        message_log_path: The path to the file used to log non-error messages (INFO through WARNING levels). If not
            provided (set to None), logging non-debug messages will be disabled.
        error_log_path: The path to the file used to log errors (messages at or above ERROR level). If not provided
            (set to None), logging errors will be disabled.
        break_long_words: Determines whether to break long words when formatting the text block to fit the width
            requirement.
        break_on_hyphens: Determines whether to break sentences on hyphens when formatting the text block to fit the
            width requirement.
        use_color: Determines whether to colorize the terminal output. This primarily applies to loguru backend.

    Attributes:
        _line_width: Stores the maximum allowed text block line width, in characters.
        _break_long_words: Determines whether to break text on long words.
        _break_on_hyphens: Determines whether to break text on hyphens.
        _use_color: Determines whether to colorize terminal-printed and file-logged text.
        _valid_extensions: Stores valid log-file extensions. This is used to verify input log file paths, as valid paths
            are expected to end with one of the supported extensions.
        _debug_log_path: Stores the path to the debug log file.
        _message_log_path: Stores the path to the message log file.
        _error_log_path: Stores the path to the error log file.
        _backend: Stores the backend option used to provide the terminal-printing and file-logging functionality.
        _logger: When logging backend is set to LOGURU, stores the instance of the loguru 'Logger' class. Otherwise, it
            is set to None.
        _is_enabled: Tracks whether logging through this class instance is enabled. When this tracker is False, echo()
            and print() methods will have limited or no functionality.

    Raises:
        ValueError: If any of the provided log file paths is not valid.
        ValidationError: If any of the input arguments are not of a valid type.
    """
    _line_width: Incomplete
    _break_long_words: Incomplete
    _break_on_hyphens: Incomplete
    _use_color: Incomplete
    _valid_extensions: Incomplete
    _debug_log_path: Incomplete
    _message_log_path: Incomplete
    _error_log_path: Incomplete
    _backend: Incomplete
    _logger: Incomplete
    _is_enabled: bool
    def __init__(self, logger_backend: Literal[LogBackends.LOGURU, LogBackends.CLICK] = ..., debug_log_path: Path | str | None = None, message_log_path: Path | str | None = None, error_log_path: Path | str | None = None, line_width: int = 120, break_long_words: bool = False, break_on_hyphens: bool = False, use_color: bool = True) -> None: ...
    def add_handles(self, *, remove_existing_handles: bool = True, debug_terminal: bool = False, debug_file: bool = False, message_terminal: bool = True, message_file: bool = False, error_terminal: bool = True, error_file: bool = False, enqueue: bool = False) -> None:
        """(Re)configures the local loguru 'logger' instance to use requested handles after optionally removing all
        existing handles.

        This method is only used when Console uses 'loguru' backend. It has no effect for other backends.

        The handles control which messages (levels) can be processed and where they are sent (terminal, file, or both).
        This method adds two separate handles to save messages to files and print them to the terminal
        for each of the 3 supported level categories: at or below DEBUG, INFO through WARNING, and at or above ERROR.
        Overall, this means the method can add up to 6 handles.

        This method only needs to be called once and only from the highest level of the call hierarchy, such as the
        main runtime script or module. Do not call this method from libraries designed to be used in other projects to
        avoid interfering with upstream processes instantiating their own handles.

        Notes:
            The method can be flexibly configured to only add a subset of all supported handles. For example,
            by default, it does not add debug handles, making it impossible to terminal-print or file-log debug
            messages. It can also be configured to not remove existing handles (default behavior) if necessary. See
            argument docstrings below for more information.

            During runtime, handles determine what happens to the message passed via the appropriate 'log' call. Loguru
            shares the set of handles across all 'logger' instances, which means this method should be used with
            caution, as it can interfere with any other handles, including the default ones.

        Args:
            remove_existing_handles: Determines whether to remove all existing handles before adding new loguru handles.
                Since loguru comes with 'default' handles enabled, this is almost always the recommended option.
            debug_terminal: Determines whether to add the handle that prints messages at or below DEBUG level to
                terminal.
            debug_file: Determines whether to add the handle that writes messages at or below DEBUG level to debug-log
                file.
            message_terminal: Same as debug_terminal, but for messages at INFO through WARNING levels.
            message_file: Same as debug_file, but for messages at INFO through WARNING levels.
            error_terminal: Same as debug_terminal, but for messages at or above ERROR level.
            error_file: Same as debug_file, but for messages at or above ERROR level.
            enqueue: Determines if messages are processed synchronously or asynchronously. Generally, this option is
                only suggested for multiprocessing runtimes that handle messages from multiple processes, as queueing
                messages prevents common multiprocessing / multithreading issues such as race conditions.

        Raises:
            ValidationError: If any of the input arguments are not of a valid type.
        """
    def enable(self) -> None:
        """Enables processing messages and errors with this Console class."""
    def disable(self) -> None:
        """Disables processing messages and errors with this Console class.

        Notes:
            Even when console is disabled, the error() method will still raise exceptions, but will not log them to
            files or provide detailed traceback information.
        """
    @property
    def get_debug_log_path(self) -> Path | None:
        """Returns the path to the log file used to save messages at or below DEBUG level or None if the path was not
        set."""
    def set_debug_log_path(self, path: Path) -> None:
        """Sets the path to the log file used to save messages at or below DEBUG level.

        Notes:
            Remember to call add_handles() method to reconfigure the handles after providing the new path when using
            loguru backend.

        Raises:
            ValueError: If the provided path does not end with one of the supported file-extensions.
        """
    @property
    def get_message_log_path(self) -> Path | None:
        """Returns the path to the log file used to save messages at INFO through WARNING levels or None if the path
        was not set."""
    def set_message_log_path(self, path: Path) -> None:
        """Sets the path to the log file used to save messages at INFO through WARNING levels.

        Notes:
            Remember to call add_handles() method to reconfigure the handles after providing the new path when using
            loguru backend.

        Raises:
            ValueError: If the provided path does not end with one of the supported file-extensions.
        """
    @property
    def get_error_log_path(self) -> Path | None:
        """Returns the path to the log file used to save messages at or above ERROR level or None if the path was not
        set."""
    def set_error_log_path(self, path: Path) -> None:
        """Sets the path to the log file used to save messages at or above ERROR level.

        Notes:
            Remember to call add_handles() method to reconfigure the handles after providing the new path when using
            loguru backend.

        Raises:
            ValueError: If the provided path does not end with one of the supported file-extensions.
        """
    @property
    def has_handles(self) -> bool:
        """Returns True if the class uses loguru backend and the backend has configured handles.

        If the class does not use loguru backend or if the class uses loguru and does not have handles, returns
        False."""
    @property
    def is_enabled(self) -> bool:
        """Returns True if logging with this Console class instance is enabled."""
    @staticmethod
    def _ensure_directory_exists(path: Path) -> None:
        """Determines if the directory portion of the input path exists and, if not, creates it.

        When the input path ends with an .extension (indicating a file path), the file portion is ignored and
        only the directory path is evaluated.

        Args:
            path: The path to be processed. Can be a file or a directory path.
        """
    def format_message(self, message: str, *, loguru: bool = False) -> str:
        """Formats the input message string according to the class configuration parameters.

        This method is generally intended to be used internally as part of the echo() or error() method runtimes.
        However, it can also be accessed and used externally to maintain consistent text formatting across the
        application.

        Args:
            message: The text string to format according to class configuration parameters.
            loguru: A flag that determines if the message is intended to be subsequently processed via loguru backend or
                another method or backend (e.g.: Exception class or CLICK backend).

        Returns:
            Formatted text message (augmented with newline and other service characters as necessary).

        Raises:
            ValidationError: If any of the arguments are not of a valid type.
        """
    def echo(self, message: str, level: LogLevel = ..., *, terminal: bool = True, log: bool = True) -> bool:
        """Formats the input message according to the class configuration and outputs it to the terminal, file, or both.

        In a way, this can be seen as a better 'print'. Specifically, in addition to printing the text to the terminal,
        this method supports colored output and can simultaneously print the message to the terminal and write it to a
        log file.

        Args:
            message: The message to be processed.
            level: The severity level of the message. This method supports all levels available through the LogLevel
                enumeration, but is primarily intended to be used for DEBUG, INFO, SUCCESS, and WARNING messages.
                Errors should be raised through the error() method when possible.
            terminal: The flag that determines whether the message should be printed to the terminal using the class
                logging backend. For loguru backend, this acts on top of the handle configuration. If there are no
                handles to print the message to the terminal, the value of this flag is ignored.
            log: The flag that determines whether the message should be written to a log file using the class logging
                backend. For loguru backend, this acts on top of the handle configuration. If there are no
                handles to save the message to a log file, the value of this flag is ignored. Note, the handle
                configuration is in turn dependent on whether valid log file path(s) were provided to the class before
                calling add_handles() method.

        Returns:
            True if the message has been processed and False if the message cannot be printed because the Console is
            disabled.

        Raises:
            ValidationError: If any of the input arguments are not of a valid type.
            RuntimeError: If the method is called while using loguru backend without any active logger handles.
        """
    def error(self, message: str, error: Callable[..., Exception] = ..., callback: Callable[[], Any] | None = ..., *, terminal: bool = True, log: bool = True, reraise: bool = False) -> None:
        """Raises the requested error.

        If Console is disabled, this method will format the error message and use the standard Python 'raise' mechanism
        to trigger the requested error. If Console is enabled, the error will be processed in-place according to
        arguments and Console backend configuration.

        Notes:
            When console is enabled, this method can be used to flexibly handle raise errors in-place. For example, it
            can be used to redirect errors to log file, provides enhanced traceback and analysis data (for loguru
            backend only) and can even execute callback functions after logging the error (also for loguru backend only.

        Args:
            message: The error-message to use for the raised error.
            error: The callable Exception class to be raised by the method.
            callback: Optional, only for loguru logging backends. The function to call after catching the raised
                exception. This can be used to terminate or otherwise alter the runtime without relying on the standard
                Python mechanism of retracing the call stack. For example, the default callback terminates the runtime
                in-place, without allowing Python to retrace the call stack that is already traced by loguru.
            terminal: The flag that determines whether the error should be printed to the terminal using the class
                logging backend. For loguru backend, this acts on top of the handle configuration. If there are no
                handles to print the error to the terminal, the value of this flag is ignored.
            log: The flag that determines whether the error should be written to a log file using the class logging
                backend. For loguru backend, this acts on top of the handle configuration. If there are no
                handles to save the error to log file, the value of this flag is ignored. Note, the handle
                configuration is in turn dependent on whether valid log file path(s) were provided to the class before
                calling add_handles() method.
            reraise: The flag that determines whether to reraise the error after it is caught and handled by
                the logging backend. For non-loguru backends, this determines if the error is raised in the first place
                or if the method only logs the error message. This option is primarily intended for runtimes that
                contain error-handling logic that has to be run in-addition to logging and tracing the error, such as
                pytest or similar frameworks.

        Raises:
            ValidationError: If any of the inputs are not of a valid type.
            RuntimeError: If the method is called while using loguru backend without any active logger handles.
        """
