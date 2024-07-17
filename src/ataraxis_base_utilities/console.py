"""This module contains the Console class that provides message and error terminal-printing and file-logging
functionality.

The Console class provides a flexible and opinionated interface that allows formatting messages and errors and printing
them to terminal or writing them to log files. Additionally, it contains enumerations and standalone functions that are
used to support Console class runtimes.
"""

import sys
from enum import Enum
from types import NoneType
from typing import Any, Literal, Optional
from pathlib import Path
import textwrap
from dataclasses import fields, dataclass
from collections.abc import Callable

import click
from loguru import logger


def default_callback(__error: str | int | None = None) -> Any:
    """Calls sys.exit() with a minimal explanation message.

    This is a wrapper over sys.exit() that can be used as the input to 'onerror' argument of loguru catch() method.
    The main advantage of using this callback over the plain sys.exit is that it avoids reprinting the exception
    message, reducing the output clutter.
    """
    sys.exit("Runtime aborted.")


class LogLevel(Enum):
    """Maps valid literal arguments that can be passed to some Console class methods to programmatically callable
    variables.

    Use this enumeration instead of 'hardcoding' logging levels where possible to automatically adjust to future API
    changes of this library.

    Log level determines the 'severity' of the logged messages. In turn, this is used to conditionally filter incoming
    messages, depending on the configuration of the Console class loguru backend. For example, the end-user can disable
    the handles for 'DEBUG' level messages and suppress any message at or below DEBUG level.
    """

    DEBUG: str = "debug"
    """
    Messages that are not shown by default and need to be purposefully enabled. These messages can be left
    in source code during early project stages to speed-up debugging, but, ideally, should be removed for mature
    projects.
    """
    INFO: str = "info"
    """
    General information messages, such as reporting the progress of a runtime.
    """
    SUCCESS: str = "success"
    """
    Runtime-ending messages specifically informing that a runtime ran successfully.
    """
    WARNING: str = "warning"
    """
    Non-runtime-breaking, but potentially problematic messages, such as deprecation warnings.
    """
    ERROR: str = "error"
    """
    Typically used when dealing with exceptions. Report runtime-breaking errors and are typically augmented with 
    traceback information.
    """
    CRITICAL: str = "critical"
    """
    Same as ERROR level, but more important. Critical errors are displayed using an augmented style that draws 
    end-user attention. Generally, this level is not used in most production runtimes.
    """


class LogBackends(Enum):
    """Maps valid backend options that can be used to instantiate the Console class to programmatically addressable
    variables.

    Use this enumeration to specify the backend used by the Console class to display and save logged messages to files.

    The backend determines the message and error processing engine used by the Console class. For most projects, it
    is highly advised to use the default loguru backend as it provides a more robust feature set, compared to
    'click' backend.
    """

    LOGURU: str = "loguru"
    """
    Loguru is the default backend for handling message and error printing and logging as it provides a robust set of 
    features and a high degree of customization. The Console class was primarily written to work with this backend.
    """
    CLICK: str = "click"
    """
    The backup backend, which also allows printing and logging messages and errors, but is not as robust as loguru.
    """


@dataclass
class LogExtensions:
    """Maps valid file-extension options that can be used by log file paths provided to the Console class to
    programmatically addressable variables.

    Use this class to add valid extensions to the log-file paths used as input arguments when initializing new
    Console class instances or augmenting existing Console class instances via setter methods.

    File extensions are used to determine the log file format. Extensions exposed through this class already contain
    the '.' prefix and should be appended to plain file names. For example, to add .log extension, you can use:
    f"file_name{LogExtensions.LOG}"
    """

    LOG: str = ".log"
    """
    Log file extensions should be the default for human-readable log files according to the general convention. These 
    files will behave exactly like .txt files, but their extension will further emphasize that they are log dumps.
    """
    TXT: str = ".txt"
    """
    While generally discouraged, the default text extension can also be used for log dump files. These files will behave
    like any other text file.
    """
    JSON: str = ".json"
    """
    A special log file extension that is generally preferred for logs that are intended to be parsed from software. 
    Unlike other supported extensions, .json files are not directly human-readable, but provide better support for 
    programmatically parsing the logged data.
    """

    @classmethod
    def values(cls) -> tuple[str, ...]:
        """Returns the valid extension options packaged into a tuple.

        The returned tuple is used by the Console class to validate incoming log paths.
        """
        return tuple(getattr(cls, field.name) for field in fields(cls))


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

        For LOGURU backends, make sure you call add_handles() method prior to processing messages to ensure that the
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
        debug_file: Determines whether to write messages at or below DEBUG level to debug-log file. This only works if
            a valid debug log file was provided.
        message_terminal: Same as debug_terminal, but for messages at INFO through WARNING levels.
        message_file: Same as debug_file, but for messages at INFO through WARNING levels.
        error_terminal: Same as debug_terminal, but for messages at or above ERROR level.
        error_file: Same as debug_file, but for messages at or above ERROR level.
        reraise_errors: Determines whether Console.error() method should reraise errors after they are caught and
            handled by the logging backend. For non-loguru backends, this determines if the error is raised in the first
            place or if the method only logs the error message. This option is primarily intended for runtimes that
            contain error-handling logic that has to be run in-addition to logging and tracing the error.


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
        _message_file: Tracks whether the class should write general messages to message log file.
        _error_terminal: Tracks whether the class should print errors to terminal.
        _error_file: Tracks whether the class is should write to error log file.
        _reraise: Tracks whether the class should reraise errors after they are caught and handled by the logger
            backend.
        _callback: Stores the callback function Console.error() method should call after catching the raised error.

    Raises:
        ValueError: If any of the provided log file paths is not valid. If the input line_width number is not valid.
            If the input logger backend is not one of the supported backends.
    """

    def __init__(
        self,
        logger_backend: Literal[LogBackends.LOGURU, LogBackends.CLICK] = LogBackends.LOGURU,
        debug_log_path: Optional[Path | str] = None,
        message_log_path: Optional[Path | str] = None,
        error_log_path: Optional[Path | str] = None,
        line_width: int = 120,
        error_callback: Optional[Callable[[], Any]] = default_callback,
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
    ) -> None:
        # Message formating parameters.
        if line_width <= 0:
            message = (
                f"Invalid 'line_width' argument encountered when instantiating Console class instance. "
                f"Expected a value greater than 0, but encountered {line_width}."
            )
            raise ValueError(
                textwrap.fill(
                    text=message, width=120, break_on_hyphens=break_on_hyphens, break_long_words=break_long_words
                )
            )
        self._line_width: int = line_width
        self._break_long_words: bool = break_long_words
        self._break_on_hyphens: bool = break_on_hyphens
        self._use_color: bool = use_color

        # Output control parameters.
        self._debug_terminal: bool = debug_terminal
        self._debug_file: bool = debug_file
        self._message_terminal: bool = message_terminal
        self._message_file: bool = message_file
        self._error_terminal: bool = error_terminal
        self._error_file: bool = error_file

        self._valid_extensions: tuple[str, ...] = LogExtensions.values()

        # Verifies that the input paths to log files, if any, use valid file extensions and are otherwise well-formed.
        # Stores currently supported log file extensions
        if not isinstance(debug_log_path, NoneType):
            debug_log_path = Path(debug_log_path)
            if debug_log_path.suffix not in self._valid_extensions:
                message = (
                    f"Invalid 'debug_log_path' argument encountered when instantiating Console class instance. "
                    f"Expected a path ending in a file name with one of the supported extensions:"
                    f"{', '.join(self._valid_extensions)}, but encountered {debug_log_path}."
                )
                raise ValueError(
                    textwrap.fill(
                        text=message,
                        width=self._line_width,
                        break_on_hyphens=self._break_on_hyphens,
                        break_long_words=self._break_long_words,
                    )
                )
            # If the path is valid, verifies the directory portion of the path exists and, if not, creates it.
            self._ensure_directory_exists(debug_log_path)
        else:
            # If the debug log file is not provided, ensures debug logging is disabled.
            self._debug_file = False

        if not isinstance(message_log_path, NoneType):
            message_log_path = Path(message_log_path)
            if message_log_path.suffix not in self._valid_extensions:
                message = (
                    f"Invalid 'message_log_path' argument encountered when instantiating Console class instance. "
                    f"Expected a path ending in a file name with one of the supported extensions:"
                    f"{', '.join(self._valid_extensions)}, but encountered {message_log_path}."
                )
                raise ValueError(
                    textwrap.fill(
                        text=message,
                        width=self._line_width,
                        break_on_hyphens=self._break_on_hyphens,
                        break_long_words=self._break_long_words,
                    )
                )
            self._ensure_directory_exists(message_log_path)
        else:
            # If the message log file is not provided, ensures message logging is disabled.
            self._message_file = False

        if not isinstance(error_log_path, NoneType):
            error_log_path = Path(error_log_path)
            if error_log_path.suffix not in self._valid_extensions:
                message = (
                    f"Invalid 'error_log_path' argument encountered when instantiating Console class instance. "
                    f"Expected a path ending in a file name with one of the supported extensions:"
                    f"{', '.join(self._valid_extensions)}, but encountered {error_log_path}."
                )
                raise ValueError(
                    textwrap.fill(
                        text=message,
                        width=self._line_width,
                        break_on_hyphens=self._break_on_hyphens,
                        break_long_words=self._break_long_words,
                    )
                )

            self._ensure_directory_exists(error_log_path)
        else:
            # If the error log file is not provided, ensures error logging is disabled.
            self._error_file = False

        # Writes resolved log paths (or Nones) to appropriate storage attributes.
        self._debug_log_path: Optional[Path] = debug_log_path
        self._message_log_path: Optional[Path] = message_log_path
        self._error_log_path: Optional[Path] = error_log_path

        # Internal trackers
        # Ensures logger backend is one of the supported options.
        if not isinstance(logger_backend, LogBackends):
            message = (
                f"Invalid 'logger_backend' argument encountered when instantiating Console class instance. "
                f"Expected a member of the LogBackends enumeration, but encountered {logger_backend}."
            )
            raise ValueError(
                textwrap.fill(
                    text=message,
                    width=self._line_width,
                    break_on_hyphens=self._break_on_hyphens,
                    break_long_words=self._break_long_words,
                )
            )

        # Saves the backend type to a local variable.
        self._backend = logger_backend

        # Specifies error-specific additional parameters
        self._reraise: bool = reraise_errors
        self._callback: Optional[Callable[[], Any]] = error_callback

        self._auto_handles = auto_handles

        # If automatic handle addition is enabled, adds handles to configure loguru backend.
        if auto_handles:
            self.add_handles()

        # Ensures the Console is disabled until it is manually enabled by the end-user.
        self._is_enabled: bool = False

    def __repr__(self) -> str:
        """Returns a string representation of the class instance."""
        return (
            f"Console(backend={self._backend}, has_handles={self.has_handles}, auto_handles={self._auto_handles}, "
            f"enabled={self.is_enabled}, line_width={self._line_width}, debug_terminal={self._debug_terminal}, "
            f"debug_file={self._debug_file}, message_terminal={self._message_terminal}, "
            f"message_file={self._message_file}, error_terminal={self._error_terminal}, error_file={self._error_file})"
        )

    def add_handles(
        self,
        *,
        remove_existing_handles: bool = True,
        enqueue: bool = False,
    ) -> None:
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
        # Returns immediately for non-loguru Consoles.
        if self._backend != LogBackends.LOGURU:
            return

        # If necessary, removes existing handles.
        if remove_existing_handles:
            logger.remove()

        # Debug terminal-printing handle. Filters and works for any message with the log-level at or below DEBUG.
        # Includes 'diagnose' information, which provides additional information about the objects involved in
        # generating the message.
        if self._debug_terminal:
            # noinspection LongLine
            logger.add(
                sys.stdout,
                format="<magenta>{time:YYYY-MM-DD HH:mm:ss.SSS}</magenta> | <level>{level: <8}</level> | <level>{message}</level>",
                filter=lambda record: record["level"].no <= logger.level("DEBUG").no,
                colorize=True,
                backtrace=False,
                diagnose=True,
                enqueue=enqueue,
            )

        # Message terminal-printing handle. Functions as a prettier, time-stamped print. Does not include any additional
        # information and only prints messages with level above DEBUG and up to WARNING (inclusive).
        if self._message_terminal:
            # noinspection LongLine
            logger.add(
                sys.stdout,
                format="<magenta>{time:YYYY-MM-DD HH:mm:ss.SSS}</magenta> | <level>{level: <8}</level> | <level>{message}</level>",
                filter=lambda record: logger.level("WARNING").no >= record["level"].no > logger.level("DEBUG").no,
                colorize=True,
                backtrace=False,
                diagnose=False,
                enqueue=enqueue,
            )

        # Error terminal-printing-handle. Does not include additional diagnostic information, but includes the whole
        # backtrace of the error message. It works similarly to default python error traces, but without mandatory
        # runtime termination. Works for ERROR+ level messages. Unlike other two handles, writes to
        # stderr, rather than stdout.
        if self._error_terminal:
            # noinspection LongLine
            logger.add(
                sys.stderr,
                format="<magenta>{time:YYYY-MM-DD HH:mm:ss.SSS}</magenta> | <level>{level: <8}</level> | <level>{message}</level>",
                filter=lambda record: record["level"].no > logger.level("WARNING").no,
                colorize=True,
                backtrace=True,
                diagnose=False,
                enqueue=enqueue,
            )

        # Debug file-writing handle. The only difference from the terminal handle is that it writes to a file, rather
        # than the stdout handle and that ut uses ataraxis_log tag instead of the ataraxis_shell. Debug files are
        # automatically removed after 2 days and are not compressed as they are considered temporary.
        if not isinstance(self._debug_log_path, NoneType) and self._debug_file:
            logger.add(
                self._debug_log_path,
                filter=lambda record: record["level"].no <= logger.level("DEBUG").no,
                colorize=False,
                retention="2 days",
                rotation="500 MB",
                enqueue=enqueue,
            )

        # Message file-writing handle. Functions similarly to terminal-printing handle, but prints to a file that does
        # not have a rotation window and is retained forever.
        if not isinstance(self._message_log_path, NoneType) and self._message_file:
            logger.add(
                self._message_log_path,
                filter=lambda record: logger.level("WARNING").no >= record["level"].no > logger.level("DEBUG").no,
                colorize=False,
                enqueue=enqueue,
            )

        # Error file-writing handle. Error files are rotated once they reach 100 MB and only retained for 5 days.
        # In addition to the full traceback, the logs include diagnostic information that provides data about objects
        # along the execution stack that led to an error to allow in-depth analysis of the problem.
        if not isinstance(self._error_log_path, NoneType) and self._error_file:
            logger.add(
                self._error_log_path,
                filter=lambda record: record["level"].no >= logger.level("ERROR").no,
                colorize=False,
                backtrace=True,
                diagnose=True,
                rotation="100 MB",
                retention="5 days",
                enqueue=enqueue,
            )

    def enable(self) -> None:
        """Enables processing messages and errors with this Console class."""
        self._is_enabled = True

    def disable(self) -> None:
        """Disables processing messages and errors with this Console class.

        Notes:
            Even when console is disabled, the error() method will still raise exceptions, but will not log them to
            files or provide detailed traceback information.
        """
        self._is_enabled = False

    @property
    def debug_log_path(self) -> Path | None:
        """Returns the path to the log file used to save messages at or below DEBUG level or None if the path was not
        set."""
        return self._debug_log_path

    def set_debug_log_path(self, path: Path) -> None:
        """Sets the path to the log file used to save messages at or below DEBUG level.

        Notes:
            Remember to call add_handles() method to reconfigure the handles after providing the new path when using
            loguru backend.

        Raises:
            ValueError: If the provided path does not end with one of the supported file-extensions.
        """
        # Verifies tha the path points ot a valid file
        if path.suffix not in self._valid_extensions:
            message = (
                f"Invalid 'path' argument encountered when setting Console debug_log_path. "
                f"Expected a path ending in a file name with one of the supported extensions:"
                f"{', '.join(self._valid_extensions)}, but encountered {path}."
            )
            raise ValueError(
                textwrap.fill(
                    text=message,
                    width=self._line_width,
                    break_on_hyphens=self._break_on_hyphens,
                    break_long_words=self._break_long_words,
                )
            )

        # Ensures that the directory included in the path exists and overwrites the local debug log path
        self._ensure_directory_exists(path)
        self._debug_log_path = path

        if self._auto_handles:
            self.add_handles(remove_existing_handles=True)

    @property
    def message_log_path(self) -> Path | None:
        """Returns the path to the log file used to save messages at INFO through WARNING levels or None if the path
        was not set."""
        return self._message_log_path

    def set_message_log_path(self, path: Path) -> None:
        """Sets the path to the log file used to save messages at INFO through WARNING levels.

        Notes:
            Remember to call add_handles() method to reconfigure the handles after providing the new path when using
            loguru backend.

        Raises:
            ValueError: If the provided path does not end with one of the supported file-extensions.
        """
        if path.suffix not in self._valid_extensions:
            message = (
                f"Invalid 'path' argument encountered when setting Console message_log_path. "
                f"Expected a path ending in a file name with one of the supported extensions:"
                f"{', '.join(self._valid_extensions)}, but encountered {path}."
            )
            raise ValueError(
                textwrap.fill(
                    text=message,
                    width=self._line_width,
                    break_on_hyphens=self._break_on_hyphens,
                    break_long_words=self._break_long_words,
                )
            )

        # Ensures that the directory included in the path exists and overwrites the local message log path
        self._ensure_directory_exists(path)
        self._message_log_path = path

        if self._auto_handles:
            self.add_handles(remove_existing_handles=True)

    @property
    def error_log_path(self) -> Path | None:
        """Returns the path to the log file used to save messages at or above ERROR level or None if the path was not
        set."""
        return self._error_log_path

    def set_error_log_path(self, path: Path) -> None:
        """Sets the path to the log file used to save messages at or above ERROR level.

        Notes:
            Remember to call add_handles() method to reconfigure the handles after providing the new path when using
            loguru backend.

        Raises:
            ValueError: If the provided path does not end with one of the supported file-extensions.
        """
        if path.suffix not in self._valid_extensions:
            message = (
                f"Invalid 'path' argument encountered when setting Console error_log_path. "
                f"Expected a path ending in a file name with one of the supported extensions:"
                f"{', '.join(self._valid_extensions)}, but encountered {path}."
            )
            raise ValueError(
                textwrap.fill(
                    text=message,
                    width=self._line_width,
                    break_on_hyphens=self._break_on_hyphens,
                    break_long_words=self._break_long_words,
                )
            )

        # Ensures that the directory included in the path exists and overwrites the local error log path
        self._ensure_directory_exists(path)
        self._error_log_path = path

        if self._auto_handles:
            self.add_handles(remove_existing_handles=True)

    @property
    def has_handles(self) -> bool:
        """Returns True if the class uses loguru backend and the backend has configured handles.

        If the class does not use loguru backend or if the class uses loguru and does not have handles, returns
        False.
        """
        if self._backend == LogBackends.LOGURU:
            # noinspection PyProtectedMember,PyUnresolvedReferences
            return len(logger._core.handlers) > 0  # type: ignore
        else:
            return False

    @property
    def is_enabled(self) -> bool:
        """Returns True if logging with this Console class instance is enabled."""
        return self._is_enabled

    @property
    def debug_terminal(self) -> bool:
        """Returns True if printing messages at or below DEBUG level to terminal is allowed."""
        return self._debug_terminal

    def set_debug_terminal(self, enabled: bool) -> None:
        """Sets the value of the debug_terminal attribute to the specified value."""
        self._debug_terminal = enabled

        if self._auto_handles:
            self.add_handles(remove_existing_handles=True)

    @property
    def debug_file(self) -> bool:
        """Returns True if writing messages at or below DEBUG level to log file is allowed."""
        return self._debug_file

    def set_debug_file(self, enabled: bool) -> None:
        """Sets the value of the debug_file attribute to the specified value."""
        self._debug_file = enabled

        if self._auto_handles:
            self.add_handles(remove_existing_handles=True)

    @property
    def message_terminal(self) -> bool:
        """Returns True if printing messages between INFO and WARNING levels to terminal is allowed."""
        return self._message_terminal

    def set_message_terminal(self, enabled: bool) -> None:
        """Sets the value of the message_terminal attribute to the specified value."""
        self._message_terminal = enabled

        if self._auto_handles:
            self.add_handles(remove_existing_handles=True)

    @property
    def message_file(self) -> bool:
        """Returns True if writing messages between INFO and WARNING levels to log file is allowed."""
        return self._message_file

    def set_message_file(self, enabled: bool) -> None:
        """Sets the value of the message_file attribute to the specified value."""
        self._message_file = enabled

        if self._auto_handles:
            self.add_handles(remove_existing_handles=True)

    @property
    def error_terminal(self) -> bool:
        """Returns True if printing messages at or above ERROR level to terminal is allowed."""
        return self._error_terminal

    def set_error_terminal(self, enabled: bool) -> None:
        """Sets the value of the error_terminal attribute to the specified value."""
        self._error_terminal = enabled

        if self._auto_handles:
            self.add_handles(remove_existing_handles=True)

    @property
    def error_file(self) -> bool:
        """Returns True if writing messages at or above ERROR level to log file is allowed."""
        return self._error_file

    def set_error_file(self, enabled: bool) -> None:
        """Sets the value of the error_file attribute to the specified value."""
        self._error_file = enabled

        if self._auto_handles:
            self.add_handles(remove_existing_handles=True)

    def set_callback(self, callback: Optional[Callable[[], Any]]) -> None:
        """Sets the class _callback attribute to the provided callback function."""
        self._callback = callback

    @property
    def reraise(self) -> bool:
        """Returns True if Console.error() method should reraise logged error messages."""
        return self._reraise

    def set_reraise(self, enabled: bool) -> None:
        """Sets the value of the reraise attribute to the specified value."""
        self._reraise = enabled

    @staticmethod
    def _ensure_directory_exists(path: Path) -> None:
        """Determines if the directory portion of the input path exists and, if not, creates it.

        When the input path ends with an .extension (indicating a file path), the file portion is ignored and
        only the directory path is evaluated.

        Args:
            path: The path to be processed. Can be a file or a directory path.
        """
        # If the path is a file (because it has a .extension suffix), ensures the parent directory of the file, if any,
        # exists.
        if path.suffix != "":
            path.parent.mkdir(parents=True, exist_ok=True)
        else:
            # If the path is a directory path, ensures the directory exists.
            path.mkdir(parents=True, exist_ok=True)

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

        # For loguru-processed messages, uses a custom formatting that accounts for the prepended header. The header
        # is assumed to be matching the standard defined in add_handles() method, which statically reserves 37
        # characters of the first line.
        if loguru:
            # Calculates indent and dedent parameters for the lines
            first_line_width: int = self._line_width - 37  # Makes the first line shorter
            subsequent_indent: str = " " * 37
            lines: list[str] = []

            # Handles the first line by wrapping it to fit into the required width given the additional loguru header.
            first_line: str = message[:first_line_width]  # Subtracts loguru header
            if len(message) > first_line_width:  # Determines the wrapping point
                # Finds the last space in the first line to avoid breaking words
                last_space: int = first_line.rfind(" ")
                if last_space != -1:  # Wraps the line
                    first_line = first_line[:last_space]

            lines.append(first_line)

            # Wraps the rest of the message by statically calling textwrap.fill on it with precalculated indent to align
            # the text to the first line.
            rest_of_message: str = message[len(first_line) :].strip()
            if rest_of_message:
                subsequent_lines = textwrap.fill(
                    rest_of_message,
                    width=self._line_width,
                    initial_indent=subsequent_indent,
                    subsequent_indent=subsequent_indent,
                    break_long_words=self._break_long_words,
                    break_on_hyphens=self._break_on_hyphens,
                )
                lines.extend(subsequent_lines.splitlines())

            return "\n".join(lines)

        # For non-loguru-processed messages, simply wraps the message via textwrap.
        else:
            return textwrap.fill(
                text=message,
                width=self._line_width,
                break_long_words=self._break_long_words,
                break_on_hyphens=self._break_on_hyphens,
            )

    def echo(self, message: str, level: LogLevel = LogLevel.INFO) -> bool:
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

        # If the Console is disabled, returns False
        if not self.is_enabled:
            return False

        # Loguru backend
        if self._backend == LogBackends.LOGURU:
            if not self.has_handles:
                message = (
                    f"Unable to echo the requested message. The Console class is configured to use the loguru backend, "
                    f"but it does not have any handles. Call add_handles() method to add handles or disable() to "
                    f"disable Console operation. The message that was attempted to be echoed: {message}"
                )
                raise RuntimeError(
                    textwrap.fill(
                        text=message,
                        width=self._line_width,
                        break_on_hyphens=self._break_on_hyphens,
                        break_long_words=self._break_long_words,
                    )
                )

            # Formats the message to work with additional loguru-prepended header.
            formatted_message = self.format_message(message=message, loguru=True)

            # For loguru, the message just needs to be logged. Loguru will use available handles to determine where to
            # route the message. The handles are, in turn, configured to match the class configuration to determine
            # the allowed output format.
            if level == LogLevel.DEBUG:
                logger.debug(formatted_message)
            elif level == LogLevel.INFO:
                logger.info(formatted_message)
            elif level == LogLevel.SUCCESS:
                logger.success(formatted_message)
            elif level == LogLevel.WARNING:
                logger.warning(formatted_message)
            elif level == LogLevel.ERROR:
                logger.error(formatted_message)
            elif level == LogLevel.CRITICAL:
                logger.critical(formatted_message)

        elif self._backend == LogBackends.CLICK:
            # Formats the message using non-loguru parameters
            formatted_message = self.format_message(message=message, loguru=False)

            # For click, terminal and log file inputs are processed separately
            if level == LogLevel.DEBUG and self._debug_terminal:
                click.secho(message=formatted_message, err=False, color=self._use_color, fg="cyan")
            elif level == LogLevel.INFO and self._message_terminal:
                click.secho(message=formatted_message, err=False, color=self._use_color, fg="white")
            elif level == LogLevel.SUCCESS and self._message_terminal:
                click.secho(message=formatted_message, err=False, color=self._use_color, fg="green")
            elif level == LogLevel.WARNING and self._message_terminal:
                click.secho(message=formatted_message, err=False, color=self._use_color, fg="yellow")
            elif level == LogLevel.ERROR and self._error_terminal:
                click.secho(message=formatted_message, err=True, color=self._use_color, fg="red")
            elif level == LogLevel.CRITICAL and self._error_terminal:
                click.secho(message=formatted_message, err=True, color=self._use_color, fg="red", bg="white")

            # Does not use colors when writing to log files.
            if level == LogLevel.DEBUG and self._debug_log_path and self._debug_file:
                with open(file=str(self._debug_log_path), mode="a") as file:
                    click.echo(file=file, message=formatted_message, color=False)
            elif level == LogLevel.ERROR or level == LogLevel.CRITICAL and self._error_log_path and self._error_file:
                with open(file=str(self._error_log_path), mode="a") as file:
                    click.echo(file=file, message=formatted_message, color=False)
            elif self._message_log_path and self._message_file:
                with open(file=str(self._message_log_path), mode="a") as file:
                    click.echo(file=file, message=formatted_message, color=False)

        # Returns true to indicate that the message was processed.
        return True

    def error(
        self,
        message: str,
        error: Callable[..., Exception] = RuntimeError,
    ) -> None:
        """Raises the requested error.

        If Console is disabled, this method will format the error message and use the standard Python 'raise' mechanism
        to trigger the requested error. If Console is enabled, the error will be processed in-place according to
        arguments and Console backend configuration.

        Notes:
            When console is enabled, this method can be used to flexibly handle raise errors in-place. For example, it
            can be used to redirect errors to log file, provides enhanced traceback and analysis data (for loguru
            backend only) and can even execute callback functions after logging the error
            (also for loguru backend only.)

            This method uses Console properties such as error_terminal, and error_file to determine whether printing,
            logging, or both are allowed. For loguru backend, the decision depends on whether the necessary handles
            have been added (or removed) from the backend. This can either be done manually or as a co-routine of the
            setter methods used to enable and disable certain types of outputs.

        Args:
            message: The error-message to use for the raised error.
            error: The callable Exception class to be raised by the method.

        Raises:
            RuntimeError: If the method is called while using loguru backend without any active logger handles.
        """

        # Formats the error message. This does nt account for and is not intended to be parsed with loguru.
        formatted_message: str = self.format_message(message, loguru=False)

        # If the backend is loguru, raises and catches the exception with loguru
        if self._backend == LogBackends.LOGURU and self.is_enabled:
            if not self.has_handles:
                message = (
                    f"Unable to properly log the requested error. The Console class is configured to use the loguru "
                    f"backend, but it does not have any handles. Call add_handles() method to add handles or disable() "
                    f"to disable Console operation. The error that was attempted to be raised: {error} with message "
                    f"{message}"
                )
                raise RuntimeError(
                    textwrap.fill(
                        text=message,
                        width=self._line_width,
                        break_on_hyphens=self._break_on_hyphens,
                        break_long_words=self._break_long_words,
                    )
                )

            with logger.catch(reraise=self._reraise, onerror=self._callback):  # type: ignore
                # noinspection PyCallingNonCallable
                raise error(formatted_message)

            # If loguru catches the error without re-raising or runtime-ending callback, ends the method runtime to
            # avoid triggering the general error raiser at the bottom of the method block.
            return

        # If the backend is click, prints the message to the requested destinations (file, terminal or both) and
        # optionally raises the error if re-raising is requested.
        elif self._backend == LogBackends.CLICK and self.is_enabled:
            if self._error_file and self._error_log_path is not None:
                with open(file=str(self._error_log_path), mode="a") as file:
                    click.echo(file=file, message=formatted_message, color=False)
            if self._error_terminal:
                click.echo(message=formatted_message, err=True, color=self._use_color)

            # If re-raising is requested, raises the error. Otherwise, ends the runtime to avoid triggering the general
            # error raiser at the bottom of the method block.
            if self._reraise:
                raise error(formatted_message)
            else:
                return

        # With the way the rest of this class is structured, this will only be raised if all other backend-specific
        # options are exhausted OR console is disabled. Having this as an unconditional end-statement ensures errors
        # processed through console class will always be raised in some way.
        raise error(formatted_message)
