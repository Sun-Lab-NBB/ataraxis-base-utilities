from enum import StrEnum
from typing import Any
from pathlib import Path
from collections.abc import Callable as Callable

from _typeshed import Incomplete

def default_callback(__error: str | int | None = None, /) -> Any:
    """Calls sys.exit() with a minimal explanation message.

    This is a wrapper over sys.exit() that can be used as the input to 'onerror' argument of loguru catch() method.
    The main advantage of using this callback over the plain sys.exit is that it avoids reprinting the exception
    message, reducing the output clutter.
    """

def pass_callback(__error: str | int | None = None, /) -> Any:
    """A placeholder callback that does nothing.

    This is a wrapper over 'pass' statement call designed to do nothing. It can be used as the input to 'onerror'
    argument of loguru catch() method. Typically, this is used in-combination with 'reraise' argument set to True to
    make loguru error handling behave similar to the regular Python exception handling.
    """

def ensure_directory_exists(path: Path) -> None:
    """Determines if the directory portion of the input path exists and, if not, creates it.

    When the input path ends with an .extension (indicating a file path), the file portion is ignored and
    only the directory path is evaluated.

    Args:
        path: The path to be processed. Can be a file or a directory path.
    """

class LogLevel(StrEnum):
    """Maps valid literal arguments that can be passed to some Console class methods to programmatically callable
    variables.

    Use this enumeration instead of 'hardcoding' logging levels where possible to automatically adjust to future API
    changes of this library.

    Log level determines the 'severity' of the logged messages. In turn, this is used to conditionally filter incoming
    messages, depending on the configuration of the Console class loguru backend. For example, the end-user can disable
    the handles for 'DEBUG' level messages and suppress any message at or below DEBUG level.
    """

    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class LogBackends(StrEnum):
    """Maps valid backend options that can be used to instantiate the Console class to programmatically addressable
    variables.

    Use this enumeration to specify the backend used by the Console class to display and save logged messages to files.

    The backend determines the message and error processing engine used by the Console class. For most projects, it
    is highly advised to use the default loguru backend as it provides a more robust feature set, compared to
    'click' backend.
    """

    LOGURU = "loguru"
    CLICK = "click"

class LogExtensions(StrEnum):
    """Maps valid file-extension options that can be used by log file paths provided to the Console class to
    programmatically addressable variables.

    Use this class to add valid extensions to the log-file paths used as input arguments when initializing new
    Console class instances or augmenting existing Console class instances via setter methods.

    File extensions are used to determine the log file format. Extensions exposed through this class already contain
    the \'.\' prefix and should be appended to plain file names. For example, to add .log extension, you can use:
    f"file_name{LogExtensions.LOG}"
    """

    LOG = ".log"
    TXT = ".txt"
    JSON = ".json"

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

        For LOGURU backends, make sure you call add_handles() method before processing messages to ensure that the
        class is properly configured to handle messages.

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
        error_callback: Optional, only for loguru logging backends. Specifies the function Console.error() method
            should call after catching the raised exception. This can be used to terminate or otherwise alter the
            runtime without relying on the standard Python mechanism of retracing the call stack. For example, the
            default callback terminates the runtime in-place, without allowing Python to retrace the call stack that is
            already traced by loguru.
        auto_handles: Determines whether to automatically call add_handles() method as necessary to ensure that loguru
            'logger' instance always matches Console class configuration. This is a dangerous option that adds a lot of
            convenience, but has the potential to interfere with all other calls to loguru. When enabled, add_handles()
            will be called after modifying class properties and automatically as part of Console class initialization.
            It is advised to never enable this option unless using Console in an interactive-environment known to not
            contain any other sources or calls to loguru logger.
        break_long_words: Determines whether to break long words when formatting the text block to fit the width
            requirement.
        break_on_hyphens: Determines whether to break sentences on hyphens when formatting the text block to fit the
            width requirement.
        use_color: Determines whether to colorize the terminal output. This primarily applies to loguru backend.
        debug_terminal: Determines whether to print messages at or below DEBUG level to terminal.
        debug_file: Determines whether to write messages at or below DEBUG level to the debug-log file. This only works
            if a valid debug log file was provided.
        message_terminal: Same as debug_terminal, but for messages at INFO through WARNING levels.
        message_file: Same as debug_file, but for messages at INFO through WARNING levels.
        error_terminal: Same as debug_terminal, but for messages at or above ERROR level.
        error_file: Same as debug_file, but for messages at or above ERROR level.
        reraise_errors: Determines whether Console.error() method should reraise errors after they are caught and
            handled by the logging backend. For non-loguru backends, this determines if the error is raised in the first
            place or if the method only logs the error message. This option is primarily intended for runtimes that
            contain error-handling logic that has to be run in-addition to logging and tracing the error.
        use_default_error_handler: Introduced in version 3.1.0. This toggle optionally overrides the error-handling
            logic to use the default Python's error-handler even when Console is enabled and uses a valid backend. This
            is used to support the runtimes that would prefer default Python error-handling, while still benefitting
            from an advanced Console backend for message logging.

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
        _is_enabled: Tracks whether logging through this class instance is enabled. When this tracker is False, echo()
            and print() methods will have limited or no functionality.
        _debug_terminal: Tracks whether the class should print debug messages to terminal.
        _debug_file: Tracks whether the class should write debug messages to debug log file.
        _message_terminal: Tracks whether the class should print general messages to terminal.
        _message_file: Tracks whether the class should write general messages to the message log file.
        _error_terminal: Tracks whether the class should print errors to terminal.
        _error_file: Tracks whether the class should write to the error log file.
        _reraise: Tracks whether the class should reraise errors after they are caught and handled by the logger
            backend.
        _callback: Stores the callback function Console.error() method should call after catching the raised error.
        _use_default_error_handler: Tracks whether the class should use the default Python error-handler.

    Raises:
        ValueError: If any of the provided log file paths is not valid. If the input line_width number is not valid.
            If the input logger backend is not one of the supported backends.
    """

    _line_width: int
    _break_long_words: bool
    _break_on_hyphens: bool
    _use_color: bool
    _debug_terminal: bool
    _debug_file: bool
    _message_terminal: bool
    _message_file: bool
    _error_terminal: bool
    _error_file: bool
    _use_default_error_handler: bool
    _valid_extensions: tuple[str, ...]
    _debug_log_path: Path | None
    _message_log_path: Path | None
    _error_log_path: Path | None
    _backend: Incomplete
    _reraise: bool
    _callback: Callable[[], Any] | None
    _auto_handles: Incomplete
    _is_enabled: bool
    def __init__(
        self,
        logger_backend: LogBackends | str = ...,
        debug_log_path: Path | str | None = None,
        message_log_path: Path | str | None = None,
        error_log_path: Path | str | None = None,
        line_width: int = 120,
        error_callback: Callable[[], Any] | None = ...,
        *,
        auto_handles: bool = False,
        break_long_words: bool = False,
        break_on_hyphens: bool = False,
        use_color: bool = True,
        debug_terminal: bool = False,
        debug_file: bool = False,
        message_terminal: bool = True,
        message_file: bool = False,
        error_terminal: bool = True,
        error_file: bool = False,
        reraise_errors: bool = False,
        use_default_error_handler: bool = False,
    ) -> None: ...
    def __repr__(self) -> str:
        """Returns a string representation of the class instance."""
    def add_handles(self, *, remove_existing_handles: bool = True, enqueue: bool = False) -> None:
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
            The method is flexibly configured to only add a subset of all supported handles, which depends on the
            Console class configuration. For example, by default, it does not add debug handles, making it impossible
            to terminal-print or file-log debug messages. It can also be configured to not remove existing handles
            (default behavior) if necessary.

            The handles added by this method depend on the Console class _debug_terminal, debug_file, message_terminal,
            message_file, error_terminal, and error_file attributes. You can access their values using property methods
            and set their values using appropriate toggle methods after class initialization.

            During runtime, handles determine what happens to the message passed via the appropriate 'log' call. Loguru
            shares the set of handles across all 'logger' instances, which means this method should be used with
            caution, as it can interfere with any other handles, including the default ones.

        Args:
            remove_existing_handles: Determines whether to remove all existing handles before adding new loguru handles.
                Since loguru comes with 'default' handles enabled, this is almost always the recommended option.
            enqueue: Determines if messages are processed synchronously or asynchronously. Generally, this option is
                only suggested for multiprocessing runtimes that handle messages from multiple processes, as queueing
                messages prevents common multiprocessing / multithreading issues such as race conditions.
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
    def debug_log_path(self) -> Path | None:
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
    def message_log_path(self) -> Path | None:
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
    def error_log_path(self) -> Path | None:
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
        False.
        """
    @property
    def enabled(self) -> bool:
        """Returns True if logging with this Console class instance is enabled."""
    @property
    def debug_terminal(self) -> bool:
        """Returns True if printing messages at or below DEBUG level to terminal is allowed."""
    def set_debug_terminal(self, enabled: bool) -> None:
        """Sets the value of the debug_terminal attribute to the specified value."""
    @property
    def debug_file(self) -> bool:
        """Returns True if writing messages at or below DEBUG level to the log file is allowed."""
    def set_debug_file(self, enabled: bool) -> None:
        """Sets the value of the debug_file attribute to the specified value."""
    @property
    def message_terminal(self) -> bool:
        """Returns True if printing messages between INFO and WARNING levels to terminal is allowed."""
    def set_message_terminal(self, enabled: bool) -> None:
        """Sets the value of the message_terminal attribute to the specified value."""
    @property
    def message_file(self) -> bool:
        """Returns True if writing messages between INFO and WARNING levels to the log file is allowed."""
    def set_message_file(self, enabled: bool) -> None:
        """Sets the value of the message_file attribute to the specified value."""
    @property
    def error_terminal(self) -> bool:
        """Returns True if printing messages at or above ERROR level to terminal is allowed."""
    def set_error_terminal(self, enabled: bool) -> None:
        """Sets the value of the error_terminal attribute to the specified value."""
    @property
    def error_file(self) -> bool:
        """Returns True if writing messages at or above ERROR level to the log file is allowed."""
    def set_error_file(self, enabled: bool) -> None:
        """Sets the value of the error_file attribute to the specified value."""
    def set_callback(self, callback: Callable[[], Any] | None) -> None:
        """Sets the class _callback attribute to the provided callback function."""
    @property
    def reraise(self) -> bool:
        """Returns True if Console.error() method should reraise logged error messages."""
    def set_reraise(self, enabled: bool) -> None:
        """Sets the value of the 'reraise' attribute to the specified value."""
    @property
    def use_default_error_handler(self) -> bool:
        """Returns True if Console.error() method should use the default Python error handler."""
    def set_use_default_error_handler(self, enabled: bool) -> None:
        """Sets the value of the 'use_default_error_handler' attribute to the specified value."""
    def format_message(self, message: str, *, loguru: bool = False) -> str:
        """Formats the input message string according to the class configuration parameters.

        This method is generally intended to be used internally as part of the echo() or error() method runtimes.
        However, it can also be accessed and used externally to maintain consistent text formatting across the
        application.

        Args:
            message: The text string to format according to class configuration parameters.
            loguru: Determines if the message is intended to be subsequently processed via loguru backend or another
                method or backend (e.g.: Exception class or CLICK backend).

        Returns:
            Formatted text message (augmented with newline and other service characters as necessary).
        """
    def echo(self, message: str, level: str | LogLevel = ...) -> bool:
        """Formats the input message according to the class configuration and outputs it to the terminal, file, or both.

        In a way, this can be seen as a better 'print'. Specifically, in addition to printing the text to the terminal,
        this method supports colored output and can simultaneously print the message to the terminal and write it to a
        log file. The exact outcome of running this method depends on the overall Console class configuration.

        Notes:
            This method uses Console properties such as message_terminal, error_terminal, and error_file to determine
            whether printing, logging, or both are allowed. For loguru backend, the decision depends on whether the
            necessary handles have been added (or removed) from the backend. This can either be done manually or as a
            co-routine of the setter methods used to enable and disable certain types of outputs.

        Args:
            message: The message to be processed.
            level: The severity level of the message. This method supports all levels available through the LogLevel
                enumeration, but is primarily intended to be used for DEBUG, INFO, SUCCESS, and WARNING messages.
                Errors should be raised through the error() method when possible.

        Returns:
            True if the message has been processed and False if the message cannot be printed because the Console is
            disabled.

        Raises:
            RuntimeError: If the method is called while using loguru backend without any active logger handles.
        """
    def error(self, message: str, error: Callable[..., Exception] = ...) -> None:
        """Raises the requested error.

        If Console is disabled, this method will format the error message and use the standard Python 'raise' mechanism
        to trigger the requested error. If Console is enabled, the error will be processed in-place according to
        arguments and Console backend configuration.

        Notes:
            When console is enabled, this method can be used to flexibly handle raised errors in-place. For example, it
            can be used to redirect errors to the log file, provides enhanced traceback and analysis data (for loguru
            backend only) and can even execute callback functions after logging the error
            (also for loguru backend only.)

            This method uses Console properties such as error_terminal, and error_file to determine whether printing,
            logging, or both are allowed. For loguru backend, the decision depends on whether the necessary handles
            have been added (or removed) from the backend. This can either be done manually or as a co-routine of the
            setter methods used to enable and disable certain types of outputs.

            Since version 3.1.0, if the Console class is configured to use default error handlers, the method will use
            the default 'raise' statement even when the Console is enabled and configured to use one of the supported
            backends.

        Args:
            message: The error-message to use for the raised error.
            error: The callable Exception class to be raised by the method.

        Raises:
            RuntimeError: If the method is called while using loguru backend without any active logger handles.
        """
