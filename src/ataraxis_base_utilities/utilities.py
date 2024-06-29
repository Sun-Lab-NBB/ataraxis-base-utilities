"""This module contains service utility classes and functions used by most packages and modules offered through this
library.

The service functions are used to provide common low-level functionality that should be unified and widely available
to all library components. The classes and functions from this module are generally not intended for use outside of
other Sun Lab projects, although they can be adopted after light reconfiguration.
"""

import os
import sys
import textwrap
import traceback
from collections.abc import Callable
from enum import Enum
from functools import wraps
from os import PathLike
from pathlib import Path
from types import NoneType
from typing import Any, Literal, Optional

import click
from loguru import logger

# noinspection PyProtectedMember
from loguru._logger import Logger
from pydantic import validate_call


class LogLevel(Enum):
    """Maps valid literal arguments that can be passed to some Console class methods to programmatically callable
    variables.

    Use this enumeration instead of 'hardcoding' logging levels where possible to automatically adjust to future API
    changes of this library.
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
    Runtime-ending messages specifically informing that the runtime ran successfully.
    """
    WARNING: str = "warning"
    """
    Non-runtime-breaking, but potentially problematic messages, such as deprecation warnings.
    """
    ERROR: str = "error"
    """
    Typically used when dealing with exceptions.
    """
    CRITICAL: str = "critical"
    """
    Errors, but more emphasized and important. Not really used in most runtimes.
    """


class LogBackends(Enum):
    """Maps valid backend options that can be used to instantiate the Console class to programmatically addressable
    variables.

    Use this enumeration to specify the backend used by the Console class to display and save logged messages to files.
    """

    LOGURU: str = "loguru"
    """
    Loguru is the default backend for handling terminal and file logging as it provides a robust set of features 
    and a high degree of customization. The Console class was primarily written to work with loguru backend.
    """
    CLICK: str = "click"
    """
    The backup backend, which provides means of printing messages to terminal and files, but is not as robust as loguru.
    """


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

    @validate_call()
    def __init__(
            self,
            logger_backend: Literal[LogBackends.LOGURU, LogBackends.CLICK] = LogBackends.LOGURU,
            message_log_path: Optional[Path | str] = None,
            error_log_path: Optional[Path | str] = None,
            debug_log_path: Optional[Path | str] = None,
            line_width: int = 120,
            break_long_words: bool = False,
            break_on_hyphens: bool = False,
            use_color: bool = True,
    ) -> None:
        # Message formating parameters.
        if line_width <= 0:
            message = (
                f"Invalid 'line_width' argument encountered when instantiating Console class instance. "
                f"Expected a value greater than 0, but encountered {line_width}."
            )
            raise ValueError(
                textwrap.fill(text=message, width=120, break_on_hyphens=break_on_hyphens,
                              break_long_words=break_long_words))
        self._line_width: int = line_width
        self._break_long_words: bool = break_long_words
        self._break_on_hyphens: bool = break_on_hyphens
        self._use_color: bool = use_color

        # Verifies that the input paths to log files, if any, use valid file extensions and are otherwise well-formed.
        valid_extensions: set[str] = {".txt", ".log", ".json"}  # Stores currently supported log file extensions
        if not isinstance(debug_log_path, NoneType):
            debug_log_path = Path(debug_log_path)
            if debug_log_path.suffix not in valid_extensions:
                message = (
                    f"Invalid 'debug_log_path' argument encountered when instantiating Console class instance. "
                    f"Expected a path ending in a file name with one of the supported extensions:"
                    f"{', '.join(valid_extensions)}, but encountered {debug_log_path}."
                )
                raise ValueError(
                    textwrap.fill(text=message, width=self._line_width, break_on_hyphens=self._break_on_hyphens,
                                  break_long_words=self._break_long_words))
            else:
                # If the path is valid, verifies the directory portion of the path exists and, if not, creates it.
                self._ensure_directory_exists(debug_log_path)
        if not isinstance(message_log_path, NoneType):
            message_log_path = Path(message_log_path)
            if message_log_path.suffix not in valid_extensions:
                message = (
                    f"Invalid 'message_log_path' argument encountered when instantiating Console class instance. "
                    f"Expected a path ending in a file name with one of the supported extensions:"
                    f"{', '.join(valid_extensions)}, but encountered {message_log_path}."
                )
                raise ValueError(
                    textwrap.fill(text=message, width=self._line_width, break_on_hyphens=self._break_on_hyphens,
                                  break_long_words=self._break_long_words))
            else:
                self._ensure_directory_exists(message_log_path)
        if not isinstance(error_log_path, NoneType):
            error_log_path = Path(error_log_path)
            if error_log_path.suffix not in valid_extensions:
                message = (
                    f"Invalid 'error_log_path' argument encountered when instantiating Console class instance. "
                    f"Expected a path ending in a file name with one of the supported extensions:"
                    f"{', '.join(valid_extensions)}, but encountered {error_log_path}."
                )
                raise ValueError(
                    textwrap.fill(text=message, width=self._line_width, break_on_hyphens=self._break_on_hyphens,
                                  break_long_words=self._break_long_words))
            else:
                self._ensure_directory_exists(error_log_path)

        self._debug_log_path: Optional[Path] = debug_log_path
        self._message_log_path: Optional[Path] = message_log_path
        self._error_log_path: Optional[Path] = error_log_path

        # Internal trackers
        self._backend = logger_backend
        if logger_backend == LogBackends.LOGURU:
            self._logger: Optional[Logger] = logger  # type: ignore
        else:
            self._logger = None
        self._is_enabled: bool = False

    @validate_call()
    def add_handles(
            self,
            *,
            remove_existing_handles: bool = True,
            debug_terminal: bool = False,
            debug_file: bool = False,
            message_terminal: bool = True,
            message_file: bool = False,
            error_terminal: bool = True,
            error_file: bool = False,
            enqueue: bool = False,
    ) -> None:
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
        # Returns immediately for non-loguru Consoles.
        if self._backend != LogBackends.LOGURU or isinstance(self._logger, NoneType):
            return

        # If necessary, removes existing handles.
        if remove_existing_handles:
            self._logger.remove()

        # Adds ataraxis_shell and ataraxis_log flags to the 'extras' dictionary passed together with each logged
        # message. These flags are used to dynamically control whether every processed message should be sent to
        # the terminal, written to the file or both.
        self._logger = self._logger.bind(ataraxis_shell=False, ataraxis_log=False)

        # Mostly here to prevent mypy being annoying, as the error is not really possible
        if isinstance(self._logger, NoneType):
            message = (
                "Unable to bind the logger to use the required extra variables. Generally, this error should not be "
                "possible"
            )
            raise RuntimeError(
                textwrap.fill(text=message, width=self._line_width, break_on_hyphens=self._break_on_hyphens,
                              break_long_words=self._break_long_words)
            )

        # Debug terminal-printing handle. Filters and works for any message with the log-level at or below DEBUG.
        # Includes 'diagnose' information, which provides additional information about the objects involved in
        # generating the message. Also uses 'ataraxis_shell' extra tag to determine if any message should be processed
        # or not.
        if debug_terminal:
            self._logger.add(
                sys.stdout,
                format="<magenta>{time:YYYY-MM-DD HH:mm:ss.SSS}</magenta> | <level>{level: <8}</level> | <level>{message}</level>",
                filter=lambda record: record["extra"]["ataraxis_terminal"] is True
                                      and record["level"].no <= logger.level("DEBUG").no,
                colorize=True,
                backtrace=False,
                diagnose=True,
                enqueue=enqueue,
            )

        # Message terminal-printing handle. Functions as a prettier, time-stamped print. Does not include any additional
        # information and only prints messages with level above DEBUG and up to WARNING (inclusive).
        if message_terminal:
            self._logger.add(
                sys.stdout,
                format="<magenta>{time:YYYY-MM-DD HH:mm:ss.SSS}</magenta> | <level>{level: <8}</level> | <level>{message}</level>",
                filter=lambda record: record["extra"]["ataraxis_terminal"] is True
                                      and logger.level("WARNING").no >= record["level"].no > logger.level("DEBUG").no,
                colorize=True,
                backtrace=False,
                diagnose=False,
                enqueue=enqueue,
            )

        # Error terminal-printing-handle. Does not include additional diagnostic information, but includes the whole
        # backtrace of the error message. It works very similar to default python error traces, but without mandatory
        # runtime termination. Works for ERROR and above level messages. Unlike other two handles, writes to
        # stderr, rather than stdout.
        if error_terminal:
            self._logger.add(
                sys.stderr,
                format="<magenta>{time:YYYY-MM-DD HH:mm:ss.SSS}</magenta> | <level>{level: <8}</level> | <level>{message}</level>",
                filter=lambda record: record["extra"]["ataraxis_terminal"] is True
                                      and record["level"].no > logger.level("WARNING").no,
                colorize=True,
                backtrace=True,
                diagnose=False,
                enqueue=enqueue,
            )

        # Debug file-writing handle. The only difference from the terminal handle is that it writes to a file, rather
        # than the stdout handle and that ut uses ataraxis_log tag instead of the ataraxis_shell. Debug files are
        # automatically removed after 2 days and are not compressed as they are considered temporary.
        if not isinstance(self._debug_log_path, NoneType) and debug_file:
            self._logger.add(
                self._debug_log_path,
                filter=lambda record: record["extra"]["ataraxis_log"] is True
                                      and record["level"].no <= logger.level("DEBUG").no,
                colorize=False,
                retention="2 days",
                rotation="500 MB",
                enqueue=enqueue,
            )

        # Message file-writing handle. Functions similarly to terminal-printing handle, but prints to a file that does
        # not have a rotation window and is retained forever.
        if not isinstance(self._message_log_path, NoneType) and message_file:
            self._logger.add(
                self._message_log_path,
                filter=lambda record: record["extra"]["ataraxis_log"] is True
                                      and logger.level("WARNING").no >= record["level"].no > logger.level("DEBUG").no,
                colorize=False,
                enqueue=enqueue,
            )

        # Error file-writing handle. Error files are rotated once they reach 100 MB and only retained for 5 days.
        # In addition to the full traceback, the logs include diagnostic information that provides data about objects
        # along the execution stack that led to an error to allow in-depth analysis of the problem.
        if not isinstance(self._error_log_path, NoneType) and error_file:
            self._logger.add(
                self._error_log_path,
                filter=lambda record: record["extra"]["ataraxis_log"] is True
                                      and record["level"].no >= logger.level("ERROR").no,
                colorize=False,
                backtrace=True,
                diagnose=True,
                rotation="100 MB",
                retention="5 days",
                enqueue=enqueue,
            )

    def enable(self) -> None:
        """A switch that enables logging messages and errors with this Console class."""
        self._is_enabled = True

    def disable(self) -> None:
        """A switch that disables logging messages and errors with this Console class."""
        self._is_enabled = False

    @property
    def has_handles(self) -> bool:
        """Returns True if the class uses LOGURU backend and the backend has configured handles.

        If the class does not use loguru backend or if the class uses loguru and does nt have handles, returns False."""
        if self._backend == LogBackends.LOGURU and not isinstance(self._logger, NoneType):
            # noinspection PyProtectedMember
            return len(self._logger._core.handlers) > 0
        else:
            return False

    @property
    def is_enabled(self) -> bool:
        """Returns True if logging with this Console class instance is enabled."""
        return self._is_enabled

    @staticmethod
    def _ensure_directory_exists(path: Path) -> None:
        """Determines if the directory portion of the input path exists and, if not, creates it.

        When the input path ends with an .extension (indicating this a file path), the file portion is ignored and
        only the directory path is evaluated.

        Args:
            path: The string-path to be processed. Should use os-defined delimiters, as os.path.splitext() is used to
                decompose the path into nodes.
        """
        # Checks if the path has an extension
        _, ext = os.path.splitext(path)

        if ext:
            # If the path has an extension, it is considered a file path. Then, extracts the directory part of the path.
            directory = os.path.dirname(path)
        else:
            # If the path doesn't have an extension, it is considered a directory path.
            directory = str(path)

        # Checks if the directory hierarchy exists.
        if not os.path.exists(directory) and directory != "":
            # If the directory hierarchy doesn't exist, creates it.
            os.makedirs(directory)

    @validate_call()
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
            rest_of_message: str = message[len(first_line):].strip()
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

    @validate_call()
    def echo(self, message: str, level: LogLevel = LogLevel.INFO, *, terminal: bool = True, log: bool = False) -> bool:
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

        # If the Console is disabled, returns False
        if not self.is_enabled:
            return False

        # Loguru backend
        if self._backend == LogBackends.LOGURU and not isinstance(self._logger, NoneType):
            if not self.has_handles:
                message = (
                    f"Unable to echo the requested message: {message}. The Console class is configured to use the "
                    f"loguru backend, but it does not have any handles. Call add_handles() method to add "
                    f"handles or disable() to disable Console operation."
                )
                raise RuntimeError(
                    textwrap.fill(text=message, width=self._line_width, break_on_hyphens=self._break_on_hyphens,
                                  break_long_words=self._break_long_words))

            # Formats the message to work with additional loguru-prepended header.
            formatted_message = self.format_message(message=message, loguru=True)

            # Logs the message using the appropriate channel and file / terminal options.
            self._logger = self._logger.bind(ataraxis_log=log, ataraxis_terminal=terminal)

            # Mostly here to prevent mypy being annoying, as the error is not really possible
            if isinstance(self._logger, NoneType):
                message = (
                    "Unable to bind the logger to use the required extra variables. Generally, this error should not be "
                    "possible"
                )
                raise RuntimeError(
                    textwrap.fill(text=message, width=self._line_width, break_on_hyphens=self._break_on_hyphens,
                                  break_long_words=self._break_long_words)
                )

            # For loguru, the message just needs to be logged. Loguru will use available handles to determine where to
            # route the message.
            if level == LogLevel.DEBUG:
                self._logger.debug(formatted_message)
            elif level == LogLevel.INFO:
                self._logger.info(formatted_message)
            elif level == LogLevel.SUCCESS:
                self._logger.success(formatted_message)
            elif level == LogLevel.WARNING:
                self._logger.warning(formatted_message)
            elif level == LogLevel.ERROR:
                self._logger.error(formatted_message)
            elif level == LogLevel.CRITICAL:
                self._logger.critical(formatted_message)

        elif self._backend == LogBackends.CLICK:
            # Formats the message using non-loguru parameters
            formatted_message = self.format_message(message=message, loguru=False)

            # For terminal, the only difference between error + and other messages is that errors go to stderr and
            # everything else goes to stdout.
            if terminal:
                if level != LogLevel.ERROR and level != LogLevel.CRITICAL:
                    click.echo(message=formatted_message, err=False, color=self._use_color)
                else:
                    click.echo(message=formatted_message, err=True, color=self._use_color)

            # For files, it is a bit more nuanced, as click respects differnt log file paths.
            if log:
                if level == LogLevel.DEBUG and self._debug_log_path:
                    with open(file=str(self._debug_log_path), mode="a") as file:
                        click.echo(file=file, message=formatted_message, color=False)

                elif level == LogLevel.ERROR or level == LogLevel.CRITICAL and self._error_log_path:
                    with open(file=str(self._error_log_path), mode="a") as file:
                        click.echo(file=file, message=formatted_message, color=False)
                elif self._message_log_path:
                    with open(file=str(self._message_log_path), mode="a") as file:
                        click.echo(file=file, message=formatted_message, color=False)

        # Returns true to indicate that the message was processed.
        return True

    @validate_call()
    def error(
            self,
            message: str,
            error: Callable[..., Exception] = RuntimeError,
            callback: Optional[Callable[[], Any]] = None,
            *,
            terminal: bool = True,
            log: bool = False,
            reraise: bool = True,
    ) -> None:
        """Raises and immediately logs the requested error.

        This method allows to flexibly raise errors, while customizing (to a degree) the way errors are logged.

        Notes:
            If Console is disabled, the method will format the message and raise the input exception using standard
            python functionality without any logging or additional features.

        Args:
            message: The error-message to pass to the error callable.
            error: The callable Exception class to be raised by the method. Defaults to RuntimeError.
            callback: Optional, only for loguru logging backends. The function to call after catching the exception.
                This can be used to terminate or otherwise alter the runtime without relying on the standard python
                mechanism of retracing the call stack. For example, sys.exit can be passed as a callable to
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

        # Formats the error message. This does nt account for and is not intended to be parsed with loguru.
        formatted_message: str = self.format_message(message, loguru=False)

        # If the class is disabled, uses regular python 'raise exception' functionality.
        if not self.is_enabled:
            raise error(formatted_message)

        # If the backend is loguru, raises and catches the exception with loguru
        if self._backend == LogBackends.LOGURU and not isinstance(self._logger, NoneType):
            if not self.has_handles:
                message = (
                    f"Unable to properly log the requested error ({error}) with message {message}. The Console class "
                    f"is configured to use the loguru backend, but it does not have any handles. Call add_handles() "
                    f"method to add handles or disable() to disable Console operation."
                )
                raise RuntimeError(
                    textwrap.fill(text=message, width=self._line_width, break_on_hyphens=self._break_on_hyphens,
                                  break_long_words=self._break_long_words))

            # Configures the logger to bind the proper flags to direct the message to log, terminal or nowhere
            self._logger = self._logger.bind(ataraxis_log=log, ataraxis_terminal=terminal)

            # Mostly here to prevent mypy being annoying, as the error is not really possible
            if isinstance(self._logger, NoneType):
                message = (
                    "Unable to bind the logger to use the required extra variables. Generally, this error should not be "
                    "possible"
                )
                raise RuntimeError(
                    textwrap.fill(text=message, width=self._line_width, break_on_hyphens=self._break_on_hyphens,
                                  break_long_words=self._break_long_words)
                )

            with self._logger.catch(reraise=reraise, onerror=callback):
                # noinspection PyCallingNonCallable
                raise error(formatted_message)

        # If the backend is click, prints the message to the requested destinations (file, terminal or both) and
        # optionally raises the error if re-raising is requested.
        elif self._backend == LogBackends.CLICK:
            if log:
                with open(file=str(self._error_log_path), mode="a") as file:
                    click.echo(file=file, message=formatted_message, color=False)
            if terminal:
                click.echo(message=formatted_message, err=True, color=self._use_color)
            if reraise:
                raise error(formatted_message)
