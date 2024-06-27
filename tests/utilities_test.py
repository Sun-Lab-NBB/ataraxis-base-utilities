"""Tests all classes and functions available from the utilities.py module."""

import pytest
from pathlib import Path
import tempfile
import os
from ataraxis_base_utilities import Console, LogLevel, LogBackends


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_initialization(backend, temp_dir):
    """Tests successful console initialization."""
    console = Console(
        logger_backend=backend,
        message_log_path=temp_dir / "message.log",
        error_log_path=temp_dir / "error.log",
        debug_log_path=temp_dir / "debug.log"
    )
    assert console._backend == backend
    assert console._message_log_path == temp_dir / "message.log"
    assert console._error_log_path == temp_dir / "error.log"
    assert console._debug_log_path == temp_dir / "debug.log"


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_invalid_line_width(backend):
    """Tests invalid line_width input during Console initialization."""
    with pytest.raises(ValueError):
        Console(logger_backend=backend, line_width=0)


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_invalid_log_path(backend, temp_dir):
    """Tests invalid path inputs during Console initialization."""

    # Specifically, uses a non-supported 'zipp' extension.
    with pytest.raises(ValueError):
        Console(logger_backend=backend, message_log_path=temp_dir / "invalid.zipp")
    with pytest.raises(ValueError):
        Console(logger_backend=backend, error_log_path=temp_dir / "invalid.zipp")
    with pytest.raises(ValueError):
        Console(logger_backend=backend, debug_log_path=temp_dir / "invalid.zipp")


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_enable_disable(backend):
    """Tests the function of the console enable / disable methods and the is_enabled property."""
    console = Console(logger_backend=backend)
    assert not console.is_enabled
    console.enable()
    assert console.is_enabled
    console.disable()
    assert not console.is_enabled


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_format_message(backend):
    console = Console(logger_backend=backend, line_width=20)
    message = "This is a long message that should be wrapped"
    formatted = console.format_message(message)
    assert len(max(formatted.split('\n'), key=len)) <= 20


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_echo(backend, temp_dir, capsys):
    console = Console(
        logger_backend=backend,
        message_log_path=temp_dir / "message.log"
    )
    console.enable()
    console.echo("Test message", LogLevel.INFO, terminal=True, log=True)
    captured = capsys.readouterr()
    assert "Test message" in captured.out
    assert os.path.exists(temp_dir / "message.log")
    with open(temp_dir / "message.log", "r") as f:
        assert "Test message" in f.read()


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_error(backend, temp_dir, capsys):
    console = Console(
        logger_backend=backend,
        error_log_path=temp_dir / "error.log"
    )
    console.enable()
    with pytest.raises(RuntimeError):
        console.error("Test error", RuntimeError, terminal=True, log=True)
    captured = capsys.readouterr()
    assert "Test error" in captured.err
    assert os.path.exists(temp_dir / "error.log")
    with open(temp_dir / "error.log", "r") as f:
        assert "Test error" in f.read()


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_error_no_reraise(backend, temp_dir, capsys):
    console = Console(
        logger_backend=backend,
        error_log_path=temp_dir / "error.log"
    )
    console.enable()
    console.error("Test error", RuntimeError, terminal=True, log=True, reraise=False)
    captured = capsys.readouterr()
    assert "Test error" in captured.err
    assert os.path.exists(temp_dir / "error.log")
    with open(temp_dir / "error.log", "r") as f:
        assert "Test error" in f.read()


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_disabled(backend, capsys):
    console = Console(logger_backend=backend)
    console.disable()
    console.echo("This should not be printed", LogLevel.INFO)
    captured = capsys.readouterr()
    assert captured.out == ""


@pytest.mark.parametrize("backend", [LogBackends.LOGURU, LogBackends.CLICK])
def test_console_add_handles(backend):
    console = Console(logger_backend=backend)
    console.add_handles()
    assert console.has_handles


def test_loguru_specific_functionality():
    console = Console(logger_backend=LogBackends.LOGURU)
    assert console._logger is not None


def test_click_specific_functionality(capsys):
    console = Console(logger_backend=LogBackends.CLICK)
    console.enable()
    console.echo("Click message", LogLevel.INFO)
    captured = capsys.readouterr()
    assert "Click message" in captured.out

# def test_format_message():
#     """Verifies correct functioning of the format-message function"""
#
#     # Verifies that a long message is formatted appropriately.
#     long_message = (
#         "This is a very long message that needs to be formatted properly. It should be wrapped at 120 characters "
#         "without breaking long words or splitting on hyphens. The formatting should be applied correctly to ensure "
#         "readability and consistency across the library."
#     )
#     # DO NOT REFORMAT. This will break the test.
#     # noinspection LongLine
#     expected_long_message = (
#         "This is a very long message that needs to be formatted properly. It should be wrapped at 120 characters without breaking\n"
#         "long words or splitting on hyphens. The formatting should be applied correctly to ensure readability and consistency\n"
#         "across the library."
#     )
#     assert format_message(long_message) == expected_long_message
#
#     # Verifies that a short message remains unaffected.
#     short_message = "This is a short message."
#     assert format_message(short_message) == short_message
#
#
# def test_format_message_error_handling():
#     """Verifies format-message error handling behavior."""
#
#     # Ensures inputting a non-string results in ValidationError
#     invalid_type = 123
#     with pytest.raises(ValidationError):
#         # noinspection PyTypeChecker
#         format_message(invalid_type)
