"""This module contains the Console class that provides message and error terminal-printing and file-logging
functionality.
"""

import sys
from enum import StrEnum
from types import NoneType
from pathlib import Path
import textwrap
from collections.abc import Callable

from loguru import logger


class LogLevel(StrEnum):
    """Stores valid logging level arguments used to configure Console.echo() method calls."""

    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogFormats(StrEnum):
    """Maps file extensions to log file formats supported by the Console class."""

    LOG = ".log"
    TXT = ".txt"
    JSON = ".json"


def ensure_directory_exists(path: Path) -> None:
    """Determines if the directory portion of the input path exists and, if not, creates it.

    Args:
        path: The path to be processed. Can be a file or a directory path.
    """
    # If the path is a file (because it has an .extension suffix), ensures the parent directory of the file, if any,
    # exists.
    if path.suffix != "":
        path.parent.mkdir(parents=True, exist_ok=True)
    else:
        # If the path is a directory path, ensures the directory exists.
        path.mkdir(parents=True, exist_ok=True)


class Console:
    """Provides methods for printing and / or logging messages and errors.

    This class wraps and extends the functionality of the 'Loguru' library to provide a centralized message handling
    interface.

    Notes:
        After initialization, call the enable() method before calling other class methods.

        Do not configure or enable the Console class from libraries that may be imported by other projects! To work
        as expected, the Console has to be enabled at the highest level of the call hierarchy.

        This class conflicts with all libraries that make explicit calls to the loguru backend, as it reconfigured
        loguru handles to support its runtime.

    Args:
        line_width: The maximum length, in characters, for a single line of displayed text. This is used to limit the
            width of the text block as it is displayed in the terminal and written to log files.
        log_directory: The path to the directory where to save the log files. Setting this argument to None disables
            the logging functionality.
        log_format: The format to use for log files. This is only used when the 'log_directory' is provided. Supported
            formats are LOG, TXT, and JSON.
        break_long_words: Determines whether to break long words when formatting the text block to fit the width
            requirement.
        break_on_hyphens: Determines whether to break sentences on hyphens when formatting the text block to fit the
            width requirement.
        debug: Determines whether to print and log debug messages.
        enqueue: Determines whether to pass logged messages through an asynchronous queue. Primarily, this is helpful
            when logging the messages from multiple producers running in parallel.

    Attributes:
        _line_width: Stores the maximum allowed text block line width, in characters.
        _break_long_words: Determines whether to break text on long words.
        _break_on_hyphens: Determines whether to break text on hyphens.
        _debug_log_path: Stores the path to the debug log file.
        _message_log_path: Stores the path to the message log file.
        _error_log_path: Stores the path to the error log file.
        _is_enabled: Tracks whether logging through this class instance is enabled. When this tracker is False, echo()
            and print() methods will have limited or no functionality.

    Raises:
        ValueError: If the input line_width number is not valid.
        TypeError: If the input log_directory is not a valid Path object.
    """

    def __init__(
        self,
        log_directory: Path | None = None,
        log_format: str | LogFormats = LogFormats.LOG,
        line_width: int = 120,
        *,
        break_long_words: bool = False,
        break_on_hyphens: bool = False,
        debug: bool = False,
        enqueue: bool = False,
    ) -> None:
        # Message formating parameters
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

        # Resolves the paths to output log files
        self._debug_log_path: Path | None = None
        self._message_log_path: Path | None = None
        self._error_log_path: Path | None = None

        # If lgo directory is provided, constructs the paths to the log files using the directory path
        if log_directory is not None:
            if not isinstance(log_directory, Path):
                message = (
                    f"Invalid 'log_directory' argument encountered when instantiating Console class instance. "
                    f"Expected a Path instance as input, but encountered {type(log_directory).__name__} instance."
                )
                raise TypeError(
                    textwrap.fill(
                        text=message, width=120, break_on_hyphens=break_on_hyphens, break_long_words=break_long_words
                    )
                )

            # If necessary, creates the log directory
            ensure_directory_exists(log_directory)

            # Ensures that the log format is one of the valid LogFormats members
            log_format = LogFormats(log_format)

            # Constructs and saves the paths to log files to class attributes.
            self._debug_log_path = log_directory / f"debug{log_format}"
            self._message_log_path = log_directory / f"message{log_format}"
            self._error_log_path = log_directory / f"error{log_format}"

        # Adds handles to configure loguru backend
        self._add_handles(debug=debug, enqueue=enqueue)

        # Ensures the Console is disabled until it is manually enabled by the user
        self._is_enabled: bool = False

    def __repr__(self) -> str:
        """Returns a string representation of the class instance."""
        return f"Console(enabled={self.enabled}, line_width={self._line_width})"

    def _add_handles(
        self,
        *,
        debug: bool = False,
        enqueue: bool = False,
    ) -> None:
        """(Re)configures the local loguru 'logger' instance to use requested handles after optionally removing all
        existing handles.

        This worker method is used internally as part of class instantiation to configure the loguru backend.

        Args:
            debug: Determines whether to enable debug handles.
            enqueue: Determines if messages are processed synchronously or asynchronously.
        """
        # Removes existing handles.
        logger.remove()

        # Debug terminal-printing handle.
        if debug:
            logger.add(
                sys.stdout,
                format=(
                    "<magenta>{time:YYYY-MM-DD HH:mm:ss.SSS}</magenta> | "
                    "<level>{level: <8}</level> | <level>{message}</level>"
                ),
                filter=lambda record: record["level"].no <= logger.level("DEBUG").no,
                colorize=True,
                backtrace=False,
                diagnose=True,
                enqueue=enqueue,
            )

        # Message terminal-printing handle.
        # noinspection LongLine
        logger.add(
            sys.stdout,
            format=(
                "<magenta>{time:YYYY-MM-DD HH:mm:ss.SSS}</magenta> | "
                "<level>{level: <8}</level> | <level>{message}</level>"
            ),
            filter=lambda record: logger.level("WARNING").no >= record["level"].no > logger.level("DEBUG").no,
            colorize=True,
            backtrace=False,
            diagnose=False,
            enqueue=enqueue,
        )

        # Error terminal-printing-handle.
        # noinspection LongLine
        logger.add(
            sys.stderr,
            format=(
                "<magenta>{time:YYYY-MM-DD HH:mm:ss.SSS}</magenta> | "
                "<level>{level: <8}</level> | <level>{message}</level>"
            ),
            filter=lambda record: record["level"].no > logger.level("WARNING").no,
            colorize=True,
            backtrace=True,
            diagnose=False,
            enqueue=enqueue,
        )

        # Handle for debug file-writing.
        if not isinstance(self._debug_log_path, NoneType) and debug:
            logger.add(
                self._debug_log_path,
                filter=lambda record: record["level"].no <= logger.level("DEBUG").no,
                colorize=False,
                rotation=None,
                retention=None,
                enqueue=enqueue,
            )

        # Message file-writing handle.
        if not isinstance(self._message_log_path, NoneType):
            logger.add(
                self._message_log_path,
                filter=lambda record: logger.level("WARNING").no >= record["level"].no > logger.level("DEBUG").no,
                colorize=False,
                enqueue=enqueue,
            )

        # Error file-writing handle.
        if not isinstance(self._error_log_path, NoneType):
            logger.add(
                self._error_log_path,
                filter=lambda record: record["level"].no >= logger.level("ERROR").no,
                colorize=False,
                backtrace=True,
                diagnose=True,
                rotation=None,
                retention=None,
                enqueue=enqueue,
            )

    def enable(self) -> None:
        """Enables processing messages and errors."""
        self._is_enabled = True

    def disable(self) -> None:
        """Disables processing messages and errors.

        Notes:
            When the console is disabled, the error() method raises exceptions, but does not log them to files or
            provides detailed traceback information.
        """
        self._is_enabled = False

    @property
    def debug_log_path(self) -> Path | None:
        """Returns the path to the log file used to save messages at or below DEBUG level or None if the path is not
        set.
        """
        return self._debug_log_path

    @property
    def message_log_path(self) -> Path | None:
        """Returns the path to the log file used to save messages at INFO through WARNING levels or None if the path
        is not set.
        """
        return self._message_log_path

    @property
    def error_log_path(self) -> Path | None:
        """Returns the path to the log file used to save messages at or above ERROR level or None if the path is not
        set.
        """
        return self._error_log_path

    @property
    def enabled(self) -> bool:
        """Returns True if the instance is configured to process messages and errors."""
        return self._is_enabled

    def format_message(self, message: str, *, loguru: bool = False) -> str:
        """Formats the input message string according to the instance configuration parameters.

        This method is primarily intended to be used internally as part of the echo() or error() method runtimes.

        Args:
            message: The text string to format.
            loguru: Determines if the message is intended to be subsequently processed via loguru backend or another
                method or backend (e.g.: Exception class).

        Returns:
            The formatted message string.
        """
        # For loguru-processed messages, uses a custom formatting that accounts for the prepended header. The header
        # is assumed to be matching the standard defined in add_handles() method, which statically reserves 37
        # characters of the first line.
        if loguru:
            # Calculates indent and dedent parameters for the lines
            first_line_width: int = self._line_width - 37  # Shortens the first line
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
        return textwrap.fill(
            text=message,
            width=self._line_width,
            break_long_words=self._break_long_words,
            break_on_hyphens=self._break_on_hyphens,
        )

    def echo(self, message: str, level: str | LogLevel = LogLevel.INFO) -> None:
        """Formats the input message according to the class configuration and outputs it to the terminal, file, or both.

        Args:
            message: The message to be processed.
            level: The severity level of the message.

        Raises:
            ValueError: If the requested log_level is not one of the valid LogLevel members.
        """
        # If the Console is disabled, returns without further processing.
        if not self.enabled:
            return

        # Formats the message to work with additional loguru-prepended header.
        formatted_message = self.format_message(message=message, loguru=True)

        # Determines the appropriate level and logs the message.
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
        else:
            message = (
                f"Unable to echo the requested message. Expected one of the levels defined in the LogLevel "
                f"enumeration as the 'level' argument, but instead encountered {level} of type {type(level).__name__}."
            )
            raise ValueError(
                textwrap.fill(
                    text=message,
                    width=self._line_width,
                    break_on_hyphens=self._break_on_hyphens,
                    break_long_words=self._break_long_words,
                )
            )

    def error(
        self,
        message: str,
        error: Callable[..., Exception] = RuntimeError,
    ) -> None:
        """Raises the requested error with integrated logging.

        If the Console class is disabled, the method raises an exception without logging. Otherwise, if file-logging is
        enabled, the method logs the error to the file before raising an exception.

        Args:
            message: The error message.
            error: The exception class to raise.
        """
        # Initializes the exception instance
        exception_instance = error(message)

        if self.enabled and self.error_log_path is not None:
            # Logs the error message at ERROR level
            formatted_message = self.format_message(message=message, loguru=True)
            log_message = f"Raising {type(exception_instance).__name__}: {formatted_message}"

            # Always logs at ERROR level
            logger.error(log_message)

        # Raises the error with clean formatting
        clean_message = self.format_message(message=message, loguru=False)
        raise error(clean_message)


# Preconfigures and exposes the Console class instance as a variable, similar to how Loguru exposes logger. This allows
# all downstream libraries to use the same Console instance when working with messages and errors.
console: Console = Console()
