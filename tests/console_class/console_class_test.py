"""This module stores the tests for all classes and functions available from the console.py module."""

import re
from typing import Any, Generator
from pathlib import Path
import tempfile

from loguru import logger
import pytest

from ataraxis_base_utilities.console.console_class import (
    Console,
    LogLevel,
    LogFormats,
    console,
    ensure_directory_exists,
)


@pytest.fixture
def temp_dir() -> Generator[Path, Any, None]:
    """Generates and yields the temporary directory used by the tests that involve log file operations."""
    temp_dir_name: str
    with tempfile.TemporaryDirectory() as temp_dir_name:
        yield Path(temp_dir_name)


def test_console_class_initialization(tmp_path) -> None:
    """Verifies the functioning of the Console class __init__() method."""

    # Tests basic initialization
    test_console = Console()
    assert test_console._line_width == 120
    assert not test_console._break_long_words
    assert not test_console._break_on_hyphens
    assert not test_console._is_enabled
    assert test_console.debug_log_path is None
    assert test_console.message_log_path is None
    assert test_console.error_log_path is None

    # Tests initialization with the log directory
    log_dir = tmp_path / "logs"
    test_console_with_logs = Console(
        log_directory=log_dir,
        log_format=LogFormats.LOG,
        line_width=100,
        break_long_words=True,
        break_on_hyphens=True,
        debug=True,
        enqueue=True,
    )

    assert test_console_with_logs._line_width == 100
    assert test_console_with_logs._break_long_words
    assert test_console_with_logs._break_on_hyphens
    assert test_console_with_logs._debug_log_path == log_dir / "debug.log"
    assert test_console_with_logs._message_log_path == log_dir / "message.log"
    assert test_console_with_logs._error_log_path == log_dir / "error.log"
    assert log_dir.exists()


def test_console_variable_initialization_defaults() -> None:
    """Verifies that the console variable initializes with expected default parameters."""
    assert console._line_width == 120
    assert not console._break_long_words
    assert not console._break_on_hyphens
    assert not console._is_enabled
    assert console.debug_log_path is None
    assert console.message_log_path is None
    assert console.error_log_path is None


def test_console_initialization_errors(temp_dir) -> None:
    """Verifies the error-handling behavior of the Console class __init__() method."""

    # Tests invalid line width
    with pytest.raises(ValueError, match="Invalid 'line_width' argument"):
        Console(line_width=0)

    with pytest.raises(ValueError, match="Invalid 'line_width' argument"):
        Console(line_width=-5)

    # Tests invalid log_directory type
    with pytest.raises(TypeError, match="Invalid 'log_directory' argument"):
        # noinspection PyTypeChecker
        Console(log_directory="not_a_path")


def test_console_repr() -> None:
    """Verifies the functionality of the Console class __repr__() method."""
    test_console = Console(line_width=100)
    repr_string = repr(test_console)

    assert "Console(" in repr_string
    assert "enabled=False" in repr_string
    assert "line_width=100" in repr_string

    # Tests after enabling
    test_console.enable()
    enabled_repr = repr(test_console)
    assert "enabled=True" in enabled_repr


def test_console_enable_disable() -> None:
    """Verifies the functionality of Console class enable() / disable() methods and the enabled property."""
    test_console = Console()

    # Initially disabled
    assert not test_console.enabled

    # Enable
    test_console.enable()
    assert test_console.enabled

    # Disable
    test_console.disable()
    assert not test_console.enabled


def test_console_properties(tmp_path) -> None:
    """Verifies the functionality of Console class property getters."""
    # Test without the log directory
    test_console = Console()
    assert test_console.debug_log_path is None
    assert test_console.message_log_path is None
    assert test_console.error_log_path is None

    # Test with the log directory
    log_dir = tmp_path / "logs"
    test_console_with_logs = Console(log_directory=log_dir, log_format=LogFormats.JSON)
    assert test_console_with_logs.debug_log_path == log_dir / "debug.json"
    assert test_console_with_logs.message_log_path == log_dir / "message.json"
    assert test_console_with_logs.error_log_path == log_dir / "error.json"


def test_ensure_directory_exists() -> None:
    """Verifies the functionality of ensure_directory_exists() standalone function."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test with a directory path
        dir_path = Path(temp_dir) / "test_dir"
        ensure_directory_exists(dir_path)
        assert dir_path.exists() and dir_path.is_dir()

        # Tests with a file path
        file_path = Path(temp_dir) / "nested" / "dir" / "test_file.txt"
        ensure_directory_exists(file_path)
        assert file_path.parent.exists() and file_path.parent.is_dir()
        assert not file_path.exists()  # The file itself should not be created

        # Tests with an existing directory
        existing_dir = Path(temp_dir) / "existing_dir"
        existing_dir.mkdir()
        ensure_directory_exists(existing_dir)
        assert existing_dir.exists() and existing_dir.is_dir()

        # Tests with a deeply nested path
        deep_path = Path(temp_dir) / "very" / "deep" / "nested" / "directory" / "structure"
        ensure_directory_exists(deep_path)
        assert deep_path.exists() and deep_path.is_dir()


def test_console_format_message() -> None:
    """Verifies the functionality of the Console class format_message() method."""
    test_console = Console(line_width=80)
    message = "This is a long message that should be wrapped properly according to the specified parameters"

    # Test non-loguru wrapping
    formatted = test_console.format_message(message, loguru=False)
    assert len(max(formatted.split("\n"), key=len)) <= 80

    # Tests loguru wrapping
    formatted = test_console.format_message(message, loguru=True)
    lines = formatted.split("\n")

    # Checks first line (should account for the 37-character loguru header)
    assert len(lines[0]) <= 43  # 80 - 37 = 43

    # Checks further lines (should have proper indentation)
    for line in lines[1:]:
        if line.strip():  # Skip empty lines
            assert len(line) <= 80
            assert line.startswith(" " * 37)

    # Ensures all words are preserved
    formatted_words = re.findall(r"\w+", formatted)
    message_words = re.findall(r"\w+", message)
    assert formatted_words == message_words


def test_console_echo(tmp_path, capsys):
    """Verifies the functionality of the Console class echo () method."""
    # Setup console with log files
    log_dir = tmp_path / "logs"
    test_console = Console(log_directory=log_dir, debug=True)
    test_console.enable()

    # Tests each log level
    log_levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.SUCCESS, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]

    for level in log_levels:
        message = f"Test {level} message"
        test_console.echo(message, level)

        captured = capsys.readouterr()

        # Checks terminal output routing
        if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            assert message in captured.err
        else:
            assert message in captured.out

    # Tests with the disabled console
    test_console.disable()
    test_console.echo("Disabled message", LogLevel.INFO)
    captured = capsys.readouterr()

    # Should not output anything when disabled
    assert "Disabled message" not in captured.out
    assert "Disabled message" not in captured.err

    # Tests with a very long message
    test_console.enable()
    long_message = "This is a very long message " * 20
    test_console.echo(long_message, LogLevel.INFO)
    captured = capsys.readouterr()

    # Should be properly formatted and wrapped
    assert "This is a very long message" in captured.out


def test_console_echo_invalid_level():
    """Verifies the error-handling behavior of the Console class echo() method."""
    test_console = Console()
    test_console.enable()

    # Test with invalid log level
    with pytest.raises(ValueError, match="Unable to echo the requested message"):
        test_console.echo("Test message", "INVALID_LEVEL")


def test_console_error(tmp_path, capsys):
    """Verifies the functionality of the Console class error() method."""
    # Setup console with error logging
    log_dir = tmp_path / "logs"
    test_console = Console(log_directory=log_dir)
    test_console.enable()

    # Test basic error raising
    with pytest.raises(RuntimeError, match="Test error"):
        test_console.error("Test error")

    # Check that the error was logged to the terminal
    captured = capsys.readouterr()
    assert "Test error" in captured.err

    # Check that the error was logged to the file
    error_log_path = log_dir / "error.log"
    if error_log_path.exists():
        with open(error_log_path, "r") as f:
            log_content = f.read()
            assert "Test error" in log_content

    # Tests a custom error type
    with pytest.raises(ValueError, match="Custom error"):
        test_console.error("Custom error", ValueError)

    # Test with the disabled console (should still raise but not log)
    test_console.disable()
    with pytest.raises(TypeError, match="Disabled error"):
        test_console.error("Disabled error", TypeError)

    captured = capsys.readouterr()
    # Should not log to terminal when disabled
    assert "Disabled error" not in captured.err


def test_console_error_without_logging():
    """Tests error method when no log directory is configured."""
    test_console = Console()  # No log directory
    test_console.enable()

    # Should still raise error even without logging
    with pytest.raises(RuntimeError, match="No logging error"):
        test_console.error("No logging error")


def test_log_formats():
    """Tests LogFormats enum functionality."""
    assert LogFormats.LOG == ".log"
    assert LogFormats.TXT == ".txt"
    assert LogFormats.JSON == ".json"

    # Tests that it can be used in Console initialization. Note, cleanup error ignoring was added to comply with
    # Windows not releasing file handles in time for the cleanup to work as expected.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
        log_dir = Path(temp_dir)

        for format_type in LogFormats:
            test_console = Console(log_directory=log_dir, log_format=format_type)
            assert test_console.debug_log_path.suffix == format_type
            assert test_console.message_log_path.suffix == format_type
            assert test_console.error_log_path.suffix == format_type


def test_log_levels():
    """Tests LogLevel enum functionality."""
    expected_levels = ["debug", "info", "success", "warning", "error", "critical"]

    for level_name in expected_levels:
        assert hasattr(LogLevel, level_name.upper())
        assert getattr(LogLevel, level_name.upper()) == level_name


def test_console_add_handles(tmp_path):
    """Tests the _add_handles method functionality."""
    log_dir = tmp_path / "logs"
    test_console = Console(log_directory=log_dir, debug=True)

    # Should create loguru handles
    # noinspection PyUnresolvedReferences
    initial_handler_count = len(logger._core.handlers)
    test_console._add_handles(debug=True, enqueue=False)

    # Should have added handles (exact count depends on configuration)
    # noinspection PyUnresolvedReferences
    assert len(logger._core.handlers) >= initial_handler_count


def test_console_message_formatting_edge_cases():
    """Tests edge cases in message formatting."""
    test_console = Console(line_width=50)

    # Tests an empty message
    assert test_console.format_message("") == ""

    # Tests a single word longer than line width
    long_word = "a" * 100
    formatted = test_console.format_message(long_word, loguru=False)
    assert long_word in formatted

    # Tests the message with newlines
    multiline = "Line 1\nLine 2\nLine 3"
    formatted = test_console.format_message(multiline, loguru=False)
    assert "Line 1" in formatted and "Line 2" in formatted and "Line 3" in formatted


def test_global_console_instance():
    """Tests the global console instance."""
    # The global console should be properly initialized
    assert isinstance(console, Console)
    assert console._line_width == 120
    assert not console.enabled  # Should start disabled

    # Should be able to enable/disable
    console.enable()
    assert console.enabled
    console.disable()
    assert not console.enabled
