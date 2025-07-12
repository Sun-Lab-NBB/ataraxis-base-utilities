"""This module stores the tests for all classes and functions available from the console.py module."""

import os
import re
import sys
from typing import Any, Generator
from pathlib import Path
import tempfile

from loguru import logger
import pytest

from ataraxis_base_utilities import (
    Console,
    LogLevel,
    LogBackends,
    LogExtensions,
    console,
    error_format,
    default_callback,
    ensure_directory_exists,
)


@pytest.fixture
def temp_dir() -> Generator[Path, Any, None]:
    """Generates and yields the temporary directory used by the tests that involve log file operations."""
    temp_dir_name: str
    with tempfile.TemporaryDirectory() as temp_dir_name:
        yield Path(temp_dir_name)


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_class_initialization(backend, tmp_path) -> None:
    """Verifies the functioning of Console class __init__() method."""

    # Defines custom callback function
    def custom_callback():
        pass

    # Sets up test log paths
    debug_log_path = tmp_path / f"debug{LogExtensions.LOG}"
    message_log_path = tmp_path / f"message{LogExtensions.TXT}"
    error_log_path = tmp_path / f"error{LogExtensions.JSON}"

    # Initializes Console with all possible attributes
    test_console = Console(
        logger_backend=backend,
        debug_log_path=debug_log_path,
        message_log_path=message_log_path,
        error_log_path=error_log_path,
        line_width=100,
        error_callback=custom_callback,
        auto_handles=True,
        break_long_words=True,
        break_on_hyphens=True,
        use_color=False,
        debug_terminal=True,
        debug_file=True,
        message_terminal=False,
        message_file=True,
        error_terminal=False,
        error_file=True,
        reraise_errors=True,
    )

    # Asserts all attributes are set correctly
    assert test_console._backend == backend
    assert test_console._debug_log_path == debug_log_path
    assert test_console._message_log_path == message_log_path
    assert test_console._error_log_path == error_log_path
    assert test_console._line_width == 100
    assert test_console._callback == custom_callback
    assert test_console._auto_handles
    assert test_console._break_long_words
    assert test_console._break_on_hyphens
    assert not test_console._use_color
    assert test_console._debug_terminal
    assert test_console._debug_file
    assert not test_console._message_terminal
    assert test_console._message_file
    assert not test_console._error_terminal
    assert test_console._error_file
    assert test_console._reraise

    # Asserts that the Console is not enabled by default
    assert not test_console._is_enabled

    # Asserts that the log directories were created
    assert debug_log_path.parent.exists()
    assert message_log_path.parent.exists()
    assert error_log_path.parent.exists()


def test_console_variable_initialization_defaults() -> None:
    """Verifies that console variable initializes with expected default parameters."""
    console_default = console
    assert console_default._backend == LogBackends.LOGURU
    assert console_default._line_width == 120
    assert console_default._callback == default_callback
    assert console_default._auto_handles
    assert not console_default._break_long_words
    assert not console_default._break_on_hyphens
    assert console_default._use_color
    assert not console_default._debug_terminal
    assert not console_default._debug_file
    assert console_default._message_terminal
    assert not console_default._message_file
    assert console_default._error_terminal
    assert not console_default._error_file
    assert not console_default._reraise


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_initialization_errors(backend, temp_dir) -> None:
    """Verifies the error-handling behavior of Console class __init__() method."""

    # Uses an invalid width of <= 0
    message = (
        f"Invalid 'line_width' argument encountered when instantiating Console class instance. "
        f"Expected a value greater than 0, but encountered {0}."
    )
    with pytest.raises(ValueError, match=error_format(message)):
        Console(logger_backend=backend, line_width=0)

    valid_extensions: tuple[str, ...] = tuple(LogExtensions)

    # Uses a non-supported 'zipp' extension to trigger ValueErrors.
    message = (
        f"Invalid 'debug_log_path' argument encountered when instantiating Console class instance. "
        f"Expected a path ending in a file name with one of the supported extensions:"
        f"{', '.join(valid_extensions)}, but encountered {temp_dir / 'invalid.zipp'}."
    )
    with pytest.raises(ValueError, match=error_format(message)):
        Console(logger_backend=backend, debug_log_path=temp_dir / "invalid.zipp")
    message = (
        f"Invalid 'message_log_path' argument encountered when instantiating Console class instance. "
        f"Expected a path ending in a file name with one of the supported extensions:"
        f"{', '.join(valid_extensions)}, but encountered {temp_dir / 'invalid.zipp'}."
    )
    with pytest.raises(ValueError, match=error_format(message)):
        Console(logger_backend=backend, message_log_path=temp_dir / "invalid.zipp")
    message = (
        f"Invalid 'error_log_path' argument encountered when instantiating Console class instance. "
        f"Expected a path ending in a file name with one of the supported extensions:"
        f"{', '.join(valid_extensions)}, but encountered {temp_dir / 'invalid.zipp'}."
    )
    with pytest.raises(ValueError, match=error_format(message)):
        Console(logger_backend=backend, error_log_path=temp_dir / "invalid.zipp")

    # Tests invalid logger backend input
    message = (
        f"Invalid 'logger_backend' argument encountered when instantiating Console class instance. "
        f"Expected a member of the LogBackends enumeration, but instead encountered {'invalid_backend'} of type str."
    )
    with pytest.raises(ValueError, match=error_format(message)):
        # noinspection PyTypeChecker
        Console(logger_backend="invalid_backend")


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_repr(backend) -> None:
    """Verifies the functionality of Console class __repr__() method."""
    # Creates a Console instance with specific parameters
    test_console = Console(
        logger_backend=backend,
        line_width=100,
        auto_handles=True,
        debug_terminal=True,
        debug_file=False,
        message_terminal=True,
        message_file=False,
        error_terminal=True,
        error_file=False,
    )

    # Gets the string representation
    repr_string = repr(test_console)

    # Check that all expected attributes are present in the string
    assert "Console(" in repr_string
    assert f"backend={backend}" in repr_string
    assert "has_handles=" in repr_string  # We can't predict this value, but we can check it's there
    assert "auto_handles=True" in repr_string
    assert "enabled=False" in repr_string  # Console is disabled by default
    assert "line_width=100" in repr_string
    assert "debug_terminal=True" in repr_string
    assert "debug_file=False" in repr_string
    assert "message_terminal=True" in repr_string
    assert "message_file=False" in repr_string
    assert "error_terminal=True" in repr_string
    assert "error_file=False" in repr_string

    # Tests after enabling the console
    test_console.enable()
    enabled_repr = repr(test_console)
    assert "enabled=True" in enabled_repr

    # Tests with different auto_handles value
    console_no_auto = Console(logger_backend=backend, auto_handles=False)
    repr_string_no_auto = repr(console_no_auto)
    assert "auto_handles=False" in repr_string_no_auto


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_add_handles(backend, tmp_path, capsys) -> None:
    """Verifies the functionality of Console class add_handles() method."""
    # Setup
    debug_log = tmp_path / "debug.log"
    message_log = tmp_path / "message.log"
    error_log = tmp_path / "error.log"
    test_console = Console(
        logger_backend=backend,
        debug_log_path=debug_log,
        message_log_path=message_log,
        error_log_path=error_log,
        debug_terminal=True,
        debug_file=True,
        message_terminal=True,
        message_file=True,
        error_terminal=True,
        error_file=True,
    )

    # Tests LOGURU backend
    if backend == LogBackends.LOGURU:
        # Tests with all handlers
        test_console.add_handles()
        # noinspection PyUnresolvedReferences
        assert len(logger._core.handlers) == 6

        # Tests with two handlers disabled
        test_console._debug_terminal = False
        test_console._message_terminal = False
        test_console.add_handles()
        # noinspection PyUnresolvedReferences
        assert len(logger._core.handlers) == 4

        # Restores all handlers
        test_console._debug_terminal = True
        test_console._message_terminal = True
        test_console.add_handles()

        # Tests each handler
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        captured = capsys.readouterr()

        # Checks terminal output
        assert "Debug message" in captured.out
        assert "Info message" in captured.out
        assert "Warning message" in captured.out
        assert "Error message" in captured.err

        # Checks file output
        debug_log_content = debug_log.read_text()
        message_log_content = message_log.read_text()
        error_log_content = error_log.read_text()

        assert "Debug message" in debug_log_content
        assert "Info message" in message_log_content
        assert "Warning message" in message_log_content
        assert "Error message" in error_log_content

        # Removes all handlers from the logger instance for the tests below to work as expected
        logger.remove()
        # noinspection PyUnresolvedReferences
        assert len(logger._core.handlers) == 0

    # Tests CLICK backend
    elif backend == LogBackends.CLICK:
        # For CLICK backend, add_handles should do nothing
        logger.remove()
        # noinspection PyUnresolvedReferences
        initial_handlers = len(logger._core.handlers)
        test_console.add_handles()
        # noinspection PyUnresolvedReferences
        assert len(logger._core.handlers) == initial_handlers

    # Tests has_handles property. Should be 0 for both backends, as loguru tests involve removing all handles and
    # click backend does not instantiate handles in the first place.
    assert not test_console.has_handles

    # Enables the console and adds handles for the tests below to work for both backends
    test_console.enable()
    test_console.add_handles()

    # Tests echo method for both backends
    test_console.echo("Test debug", LogLevel.DEBUG)
    test_console.echo("Test message", LogLevel.INFO)
    test_console.echo("Test error", LogLevel.ERROR)

    captured = capsys.readouterr()

    # Checks terminal for both backends
    assert "Test debug" in captured.out
    assert "Test message" in captured.out
    assert "Test error" in captured.err

    # Checks log files for both backends
    assert "Test debug" in debug_log.read_text()
    assert "Test message" in message_log.read_text()
    assert "Test error" in error_log.read_text()


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_enable_disable(backend) -> None:
    """Verifies the functionality of Console class enable() / disable() methods and the enabled() property."""

    # tests enable / disable methods and enabled tracker
    test_console = Console(logger_backend=backend)
    assert not test_console.enabled
    test_console.enable()
    assert test_console.enabled
    test_console.disable()
    assert not test_console.enabled

    # Verifies that echo does not process input messages when the console is disabled
    assert not test_console.echo(message="Test", level=LogLevel.INFO)


def test_debug_log_path(tmp_path) -> None:
    """Verifies the functionality of Console class debug_log_path() getter and setter methods."""
    # Tests getter when the path is not set
    assert console.debug_log_path is None

    # Tests setter and getter
    debug_path = tmp_path / "debug.log"
    console.set_debug_log_path(debug_path)
    assert console.debug_log_path == debug_path


def test_message_log_path(tmp_path) -> None:
    """Verifies the functionality of Console class message_log_path() getter and setter methods."""
    # Tests getter when the path is not set
    assert console.message_log_path is None

    # Tests setter and getter
    message_path = tmp_path / "message.log"
    console.set_message_log_path(message_path)
    assert console.message_log_path == message_path


def test_error_log_path(tmp_path) -> None:
    """Verifies the functionality of Console class error_log_path() getter and setter methods."""
    # Tests getter when the path is not set
    assert console.error_log_path is None

    # Tests setter and getter
    error_path = tmp_path / "error.log"
    console.set_error_log_path(error_path)
    assert console.error_log_path == error_path


def test_invalid_path_error_handling() -> None:
    """Verifies that Console class log path setter methods correctly raise ValueError when provided with an invalid
    path.
    """
    invalid_paths = [
        Path("invalid.zippp"),  # Invalid extension
        Path("invalid"),  # No extension
    ]

    for invalid_path in invalid_paths:
        with pytest.raises(ValueError):
            console.set_debug_log_path(invalid_path)

        with pytest.raises(ValueError):
            console.set_message_log_path(invalid_path)

        with pytest.raises(ValueError):
            console.set_error_log_path(invalid_path)


def test_ensure_directory_exists() -> None:
    """Verifies the functionality of ensure_directory_exists() standalone function."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test with a directory path
        dir_path = Path(temp_dir) / "test_dir"
        ensure_directory_exists(dir_path)
        assert dir_path.exists() and dir_path.is_dir()

        # Test with a file path
        file_path = Path(temp_dir) / "nested" / "dir" / "test_file.txt"
        ensure_directory_exists(file_path)
        assert file_path.parent.exists() and file_path.parent.is_dir()
        assert not file_path.exists()  # The file itself should not be created

        # Test with an existing directory
        existing_dir = Path(temp_dir) / "existing_dir"
        existing_dir.mkdir()
        ensure_directory_exists(existing_dir)
        assert existing_dir.exists() and existing_dir.is_dir()

        # Test with a path that includes a file in an existing directory
        existing_file_path = Path(temp_dir) / "test_file2.txt"
        ensure_directory_exists(existing_file_path)
        assert existing_file_path.parent.exists() and existing_file_path.parent.is_dir()
        assert not existing_file_path.exists()  # The file itself should not be created

        # Test with a deeply nested path
        deep_path = Path(temp_dir) / "very" / "deep" / "nested" / "directory" / "structure"
        ensure_directory_exists(deep_path)
        assert deep_path.exists() and deep_path.is_dir()


def test_console_output_attributes() -> None:
    """Verifies the functionality of Console class output (eg: debug_terminal) getter and setter methods.

    Since this uses console variable that comes with auto_handles by default, this also tests automatic handle
    adjustment.
    """
    # Debug terminal
    console.set_debug_terminal(False)
    assert not console.debug_terminal
    # noinspection PyUnresolvedReferences
    handles_1 = len(logger._core.handlers)
    console.set_debug_terminal(True)
    assert console.debug_terminal
    # noinspection PyUnresolvedReferences
    assert len(logger._core.handlers) != handles_1  # Verifies that auto_handles works as expected

    # Debug file
    console.set_debug_file(False)
    assert not console.debug_file
    console.set_debug_file(True)
    assert console.debug_file

    # Message terminal
    console.set_message_terminal(False)
    assert not console.message_terminal
    console.set_message_terminal(True)
    assert console.message_terminal

    # Message file
    console.set_message_file(False)
    assert not console.message_file
    console.set_message_file(True)
    assert console.message_file

    # Error terminal
    console.set_error_terminal(False)
    assert not console.error_terminal
    console.set_error_terminal(True)
    assert console.error_terminal

    # Error file
    console.set_error_file(False)
    assert not console.error_file
    console.set_error_file(True)
    assert console.error_file


def test_console_error_attributes(tmp_path):
    """Verifies the functionality of Console class error-specific attribute getter and setter methods."""

    # Reraise
    console.set_reraise(True)
    assert console.reraise
    console.set_reraise(False)
    assert not console.reraise

    # Callback
    def custom_callback():
        """Custom callback used for this test."""
        pass

    assert console._callback == default_callback
    console.set_callback(custom_callback)
    assert console._callback == custom_callback


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_format_message(backend) -> None:
    """Verifies the functionality of Console class format_message() method."""
    message = "This is a long message that should be wrapped properly according to the specified parameters"

    # Tests non-loguru wrapping
    formatted = console.format_message(message, loguru=False)
    assert len(max(formatted.split("\n"), key=len)) <= 120

    # Tests loguru wrapping
    formatted = console.format_message(message, loguru=True)
    lines = formatted.split("\n")

    # Checks first line (should be 83 characters or fewer due to 37-character loguru header)
    assert len(lines[0]) <= 83  # 120 - 37 = 83

    # Checks the following lines (should be 120 characters or fewer, with at least 37 characters of indentation)
    for line in lines[1:]:
        assert len(line) <= 120
        assert line.startswith(" " * 37)

    # Ensures that the wrapped message is not empty
    assert formatted.strip() != ""

    # Ensures that the entire original message is contained within the formatted version
    # We'll use a more flexible comparison that ignores spaces and newlines
    formatted_content = re.sub(r"\s+", "", formatted)
    message_content = re.sub(r"\s+", "", message)
    assert message_content in formatted_content

    # Additional check to ensure all words are present in the correct order
    formatted_words = re.findall(r"\w+", formatted)
    message_words = re.findall(r"\w+", message)
    assert formatted_words == message_words


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_echo(backend, tmp_path, capsys):
    """Verifies the functionality of Console class echo() method."""
    # Setup
    debug_log = tmp_path / "debug.log"
    message_log = tmp_path / "message.log"
    error_log = tmp_path / "error.log"

    test_console = Console(
        logger_backend=backend,
        debug_log_path=debug_log,
        message_log_path=message_log,
        error_log_path=error_log,
        debug_terminal=True,
        debug_file=True,
        message_terminal=True,
        message_file=True,
        error_terminal=True,
        error_file=True,
    )
    test_console.enable()
    test_console.add_handles()

    # Tests each log level
    log_levels = [
        (LogLevel.DEBUG, debug_log),
        (LogLevel.INFO, message_log),
        (LogLevel.SUCCESS, message_log),
        (LogLevel.WARNING, message_log),
        (LogLevel.ERROR, error_log),
        (LogLevel.CRITICAL, error_log),
    ]

    # Verifies the messages are logged and echoed correctly
    for level, log_file in log_levels:
        message = f"Test {level.name} message"
        result = test_console.echo(message, level)

        assert result is True  # echo should return True when successful

        captured = capsys.readouterr()

        if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            assert message in captured.err
        else:
            assert message in captured.out

        assert os.path.exists(log_file)
        with open(log_file, "r") as f:
            assert message in f.read()

    # Tests terminal-only output
    test_console.set_message_file(False)
    test_console.set_message_terminal(True)
    test_console.add_handles()  # This implicitly tests for no auto_handles behavior: need to call it manually
    result = test_console.echo("Terminal only", LogLevel.INFO)
    assert result
    captured = capsys.readouterr()
    assert "Terminal only" in captured.out
    with open(message_log, "r") as f:
        assert "Terminal only" not in f.read()

    # Tests both terminal and log output disabled behavior
    test_console.set_message_terminal(False)
    test_console.set_message_file(False)
    test_console.add_handles()
    result = test_console.echo("Log only", LogLevel.INFO)
    assert result
    captured = capsys.readouterr()
    assert "Log only" not in captured.out
    with open(message_log, "r") as f:
        assert "Log only" not in f.read()

    # Tests log-only output
    test_console.set_message_terminal(False)
    test_console.set_message_file(True)
    test_console.add_handles()
    result = test_console.echo("Log only", LogLevel.INFO)
    assert result
    captured = capsys.readouterr()
    assert "Log only" not in captured.out
    with open(message_log, "r") as f:
        assert "Log only" in f.read()

    # Tests disabled console behavior
    test_console.disable()
    result = test_console.echo("Disabled message", LogLevel.INFO)
    assert result is False
    captured = capsys.readouterr()
    assert "Disabled message" not in captured.out
    with open(message_log, "r") as f:
        assert "Disabled message" not in f.read()

    # Tests with a very long message and console still being disabled
    long_message = "This is a very long message " * 20
    result = test_console.echo(long_message, LogLevel.INFO)
    assert result is False  # Because console is still disabled
    captured = capsys.readouterr()
    assert long_message not in captured.out
    with open(message_log, "r") as f:
        assert long_message not in f.read()

    # Re-enables console and tests a long message again. Enables all handles too.
    test_console.enable()
    test_console.set_message_terminal(True)
    test_console.set_message_file(True)
    test_console.add_handles()
    long_message = "This is a very long message " * 20
    result = test_console.echo(long_message, LogLevel.INFO)
    assert result is True
    captured = capsys.readouterr()

    if backend == LogBackends.LOGURU:
        # Removes ANSI color codes, timestamps, and log levels
        cleaned_output = re.sub(r"\x1b\[[0-9;]*m", "", captured.out)
        cleaned_output = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} \| \w+\s+\| ", "", cleaned_output)
        # Remove extra spaces and newlines
        cleaned_output = " ".join(cleaned_output.split())
    else:  # CLICK
        # Removes extra spaces and newlines
        cleaned_output = " ".join(captured.out.split())

    # Removes extra spaces from long_message for comparison
    cleaned_long_message = " ".join(long_message.split())

    assert cleaned_long_message in cleaned_output

    # Checks log file
    with open(message_log, "r") as f:
        log_content = f.read()
        assert cleaned_long_message in " ".join(log_content.split())


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_echo_errors(backend):
    """Verifies the error-handling behavior of Console class echo() method."""

    test_console = Console(logger_backend=backend)
    logger.remove()  # Removes all handlers
    test_console.enable()  # Ensures console is enabled

    # Tests error when using Loguru backend without handles
    if backend == LogBackends.LOGURU:
        message = (
            f"Unable to echo the requested message. The Console class is configured to use the loguru backend, "
            f"but it does not have any handles. Call add_handles() method to add handles or disable() to "
            f"disable Console operation. The message that was attempted to be echoed: {'Test message'}"
        )
        with pytest.raises(RuntimeError, match=error_format(message)):
            test_console.echo("Test message", LogLevel.INFO)
    elif backend == LogBackends.CLICK:
        # Other backends should not raise any errors even if there are no handles
        test_console.echo("Test message", LogLevel.INFO)


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_error(backend, tmp_path, capsys):
    """Verifies the functionality of Console class error() method."""
    test_console = Console(logger_backend=backend, error_log_path=tmp_path / "error.log")
    test_console.enable()
    test_console.set_error_terminal(True)
    test_console.set_error_file(True)
    test_console.add_handles()

    # Tests successful error raising with no callback and reraise functionality
    test_console.set_reraise(True)
    test_console.set_callback(None)
    with pytest.raises(RuntimeError, match="Test error"):
        test_console.error(message="Test error")

    # Verifies the error has been printed and logged as expected
    captured = capsys.readouterr()
    assert "Test error" in captured.err
    assert os.path.exists(tmp_path / "error.log")
    with open(tmp_path / "error.log", "r") as f:
        assert "Test error" in f.read()

    # Tests error without 'reraise' or 'callback'. In this case, the method should log the error and end its runtime
    test_console.set_reraise(False)
    test_console.error(message="No reraise error", error=ValueError)
    captured = capsys.readouterr()
    assert "No reraise error" in captured.err
    with open(tmp_path / "error.log", "r") as f:
        assert "No reraise error" in f.read()

    # Tests raising custom errors
    class CustomError(Exception):
        pass

    test_console.set_reraise(True)
    with pytest.raises(CustomError):
        test_console.error(message="Custom error", error=CustomError)

    # Verifies the output
    captured = capsys.readouterr()
    assert "Custom error" in captured.err

    # Tests callback (only for Loguru backend)
    if backend == LogBackends.LOGURU:
        callback_called = False

        def callback_func(_error):
            nonlocal callback_called
            callback_called = True
            print("Callback executed", file=sys.stderr)

        # noinspection PyTypeChecker
        test_console.set_callback(callback_func)
        test_console.set_reraise(False)
        test_console.error("Callback error", error=ValueError)
        captured = capsys.readouterr()
        assert "Callback error" in captured.err
        assert "Callback executed" in captured.err
        assert callback_called

        # Also tests default callback performance (that it correctly aborts the runtime)
        test_console.set_reraise(False)
        test_console.set_callback(default_callback)
        with pytest.raises(SystemExit):
            test_console.error("Callback error", error=ValueError)
        _ = capsys.readouterr()  # Silences the output

    # Checks that all errors were logged
    with open(tmp_path / "error.log", "r") as f:
        log_content = f.read()
        assert "Test error" in log_content
        assert "No reraise error" in log_content
        assert "Custom error" in log_content
        if backend == LogBackends.LOGURU:
            assert "Callback error" in log_content

    # Verifies that disabled console correctly defaults to using 'standard' Python aise functionality
    test_console.disable()
    message = "Disabled Test Message"
    with pytest.raises(TypeError, match=error_format(message)):
        console.error(message=message, error=TypeError)


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_error_output_options(backend, tmp_path, capsys):
    """Verifies that Console class error() method respects class output configuration parameters."""

    # Also tests the auto-handles attribute
    error_log = tmp_path / "error.log"
    test_console = Console(logger_backend=backend, error_log_path=error_log, auto_handles=True)

    # Ensures that callbacks and reraise are disabled for this test.
    test_console.set_reraise(False)
    test_console.set_callback(None)
    test_console.enable()

    # Tests logging the error to terminal only
    test_console.set_error_terminal(True)
    test_console.set_error_file(False)
    test_console.error("Terminal only", RuntimeError)
    captured = capsys.readouterr()
    assert "Terminal only" in captured.err
    # Verifies that the log file is not created
    assert not error_log.exists()

    # Tests log only
    test_console.set_error_terminal(False)
    test_console.set_error_file(True)
    test_console.error("Log only", RuntimeError)
    captured = capsys.readouterr()
    assert captured.err == ""
    with open(tmp_path / "error.log", "r") as f:
        assert "Log only" in f.read()

    # Tests both terminal and log output disabled
    test_console.set_error_terminal(False)
    test_console.set_error_file(False)
    test_console.error("Neither", RuntimeError)
    captured = capsys.readouterr()
    assert captured.err == ""
    with open(tmp_path / "error.log", "r") as f:
        assert "Neither" not in f.read()


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_error_handling(backend, tmp_path, capsys):
    """Verifies the error-handling behavior of Console class error() method."""
    test_console = Console(logger_backend=backend, auto_handles=True, error_log_path=tmp_path / "error.log")
    test_console.enable()

    # Removes all handlers to facilitate the test below
    logger.remove()

    # Verifies that missing handles cause an error for loguru, but not other backends
    if backend == LogBackends.LOGURU:
        message = (
            f"Unable to properly log the requested error. The Console class is configured to use the loguru "
            f"backend, but it does not have any handles. Call add_handles() method to add handles or disable() "
            f"to disable Console operation. The error that was attempted to be raised: {RuntimeError} with message "
            f"{'No handles error'}"
        )
        with pytest.raises(RuntimeError, match=error_format(message)):
            test_console.error("No handles error", RuntimeError)
    else:
        test_console.error("No handles error", RuntimeError)
        _ = capsys.readouterr()  # Silences the error output
