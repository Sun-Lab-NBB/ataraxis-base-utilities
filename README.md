# ataraxis-base-utilities

A Python library that provides shared utility assets used to support most other Sun Lab projects.

![PyPI - Version](https://img.shields.io/pypi/v/ataraxis-base-utilities)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ataraxis-base-utilities)
[![uv](https://tinyurl.com/uvbadge)](https://github.com/astral-sh/uv)
[![Ruff](https://tinyurl.com/ruffbadge)](https://github.com/astral-sh/ruff)
![type-checked: mypy](https://img.shields.io/badge/type--checked-mypy-blue?style=flat-square&logo=python)
![PyPI - License](https://img.shields.io/pypi/l/ataraxis-base-utilities)
![PyPI - Status](https://img.shields.io/pypi/status/ataraxis-base-utilities)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/ataraxis-base-utilities)

___

## Detailed Description

The primary focus of this library is to provide the unified message and error processing framework used across all
other Sun lab projects instead of the built-in 'print,' 'logging,' and 'raise' assets. In addition to this framework, it
also provides functions used to perform common filesystem operations (such as creating directories) and facilitate 
efficient parallel data processing (such as chunking iterables into batches).

___

## Features

- Supports Windows, Linux, and macOS.
- Provides a unified approach to message and error formatting, printing, and logging through the Console class.
- Provides a set of common utility functions frequently reused across other Sun lab projects.
- GPL 3 License.

___

## Table of Contents

- [Dependencies](#dependencies)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Developers](#developers)
- [Versioning](#versioning)
- [Authors](#authors)
- [License](#license)
- [Acknowledgements](#Acknowledgments)

___

## Dependencies

For users, all library dependencies are installed automatically by all supported installation methods 
(see the [Installation](#installation) section).

***Note!*** Developers should see the [Developers](#developers) section for information on installing additional 
development dependencies.

___

## Installation

### Source

Note, installation from source is ***highly discouraged*** for anyone who is not an active project developer.

1. Download this repository to the local machine using the preferred method, such as git-cloning. Use one of the 
   [stable releases](https://github.com/Sun-Lab-NBB/ataraxis-base-utilities/tags) that include precompiled binary and 
   source code distribution (sdist) wheels.
2. If the downloaded distribution is stored as a compressed archive, unpack it using the appropriate decompression tool.
3. ```cd``` to the root directory of the prepared project distribution.
4. Run ```python -m pip install .``` to install the project. Alternatively, if using a distribution with precompiled
   binaries, use ```python -m pip install WHEEL_PATH```, replacing 'WHEEL_PATH' with the path to the wheel file.

### pip

Use the following command to install the library using pip: ```pip install ataraxis-base-utilities```

___

## Usage

### Console
The Console class provides a unified [loguru](https://github.com/Delgan/loguru)-based framework for working with 
messages and errors to display them in the terminal and (optionally) log them to files.

#### Quickstart
Most class functionality revolves around 2 methods: ```echo()``` and ```error()```. To make adoption as frictionless
as possible, a preconfigured Console instance is exposed as part of the library initialization via the 'console' global 
variable:
```
from ataraxis_base_utilities import console

# All class functionality is disabled by default and must be enabled for the class to behave as expected.
console.enable()

# Use this instead of 'print'!
console.echo("This is a better 'print'.")

# Use this instead of 'raise'!
console.error("This is a 'raise' with logging.")
```

***Note!*** The preconfigured class does **not** log processed messages and errors to files. To enable file-logging, 
re-initialize the Console class with the appropriate 
[configuration parameters](#overriding-default-console-configuration).

#### Working with Messages
All Console’s functionality for working with messages is realized through the **echo()** method. Depending on 
class configuration, the method can be flexibly used to display the input messages in the terminal and log them to 
files. Each message is handed according to its **LogLevel** (urgency level) and the processing Console’s configuration.
```
from ataraxis_base_utilities import console, LogLevel
console.enable()

# By default, console is configured to NOT print debug messages. Calling echo for a message at 'Debug' level has no 
# effect
console.echo(message='Debug is disabled by default.', level=LogLevel.DEBUG)

# Messages at all levels other than 'Debug' are always printed if the console is enabled.
console.echo(message='Information messages are enabled!', level=LogLevel.INFO)
console.echo(message='Error messages are enabled!', level=LogLevel.ERROR)

# Disabled console does not print any messages.
console.disable()
console.echo(message='Disabled console does not print messages.', level=LogLevel.INFO)
```

#### Working with Errors
The Console class treats errors as a special class of messages, handled through the **error()** method. Error 
messages are always handled at the **Error** log level and always interrupt the normal runtime flow of the 
caller program by calling the built-in 'raise' method after logging the message.
```
from ataraxis_base_utilities import console

# The Console raises error messages even if it is disabled. However, the instance does not log messages to files when
# disabled.
console.disable()

# Specify the exception to be raised by providing it as an 'error' argument. By default, this argument is
# set to RuntimeError.
console.error(message="Error message", error=TypeError)
```

#### Message Formatting
All Console methods format input messages to fit the Sun lab’s default width-limit of 120 characters. It is 
possible to directly access and use the formatter through the **format_message()** method:
```
from ataraxis_base_utilities import console

# This long message does not display well without additional formatting
message = (
    "This is a long message that exceeds our default limit of 120 characters. Therefore, it needs to be wrapped to "
    "appear correctly when printed to the terminal (or saved to a log file)."
)
print(message)

# Prints a line-break for easier difference visualization
print()

# This formats the message according to the current (default) Console configuration.
formatted_message = console.format_message(message)
print(formatted_message)
```

#### Overriding Default Console Configuration
The default Console instance exposed via the 'console' variable is used by all other Sun lab projects. Re-initializing 
and overriding the **console** variable overrides the Console configuration used by ***all*** Sun lab 
projects used by the same process. **Note!** Overriding the default Console configuration is a prerequisite for 
enabling logging messages and errors to files and working with 'Debug' level messages.
```
from ataraxis_base_utilities import console, Console, LogLevel, LogFormats
from pathlib import Path
from tempfile import TemporaryDirectory

# Overwriting the default 'console' instance replaces the instance used by all other Sun lab projects running in the
# same process as the overridden 'console'.
console = Console()  # This is equivalent to using the 'default' configuration

# Behaves like the default 'console' instance.
console.enable()
console.echo("Not printed by default.", level=LogLevel.DEBUG)

# Reinitializing the Console allows overriding default runtime parameters. For example, it can be used to enabled
# handling 'Debug' messages.
console = Console(debug=True)
console.enable()  # Reinitializing the console resets it to the 'disabled' state.
console.echo("Debug messages are now enabled!", level=LogLevel.DEBUG)

# Another important configuration step that requires reinitializing the console is enabling logging messages and errors
# to files, which is disabled by default.
with TemporaryDirectory() as log_directory:
    console = Console(
        log_directory=Path(log_directory),
        log_format=LogFormats.TXT,  # LogFormats enumeration stores all currently supported log file formats.
        debug=True
    )

    # Prints and saves the debug message to a log file.
    console.enable()
    console.echo("Debug messages are now logged to the debug log file!", level=LogLevel.DEBUG)

    # The message can now be viewed by reading the .txt log file.
    with console.debug_log_path.open("r") as file:
        console.echo(file.read())
```

#### Compatibility with Other Projects:
The Console class is built on top of the [loguru](https://github.com/Delgan/loguru) library. As part of its 
initialization, each Console class automatically resets the handles used by the 'logger' exposed by Loguru. Therefore, 
the Console class is **incompatible** with any other third-party library that uses Loguru for similar purposes.

### Standalone Methods
The standalone methods are a collection of utility functions that either abstract away the boilerplate code for 
common data manipulations or provide novel functionality not commonly available through popular Python libraries used 
by other Sun lab projects. Generally, these methods are straightforward to use and do not require detailed explanation.
See the API documentation below for details on available standalone methods.
___

## API Documentation

See the [API documentation](https://ataraxis-base-utilities-api-docs.netlify.app/) for the detailed description of the 
methods and classes exposed by components of this library.

___

## Developers

This section provides installation, dependency, and build-system instructions for project developers.

### Installing the Project

***Note!*** This installation method requires **mamba version 2.3.2 or above**. Currently, all Sun lab automation 
pipelines require that mamba is installed through the [miniforge3](https://github.com/conda-forge/miniforge) installer.

1. Download this repository to the local machine using the preferred method, such as git-cloning.
2. If the downloaded distribution is stored as a compressed archive, unpack it using the appropriate decompression tool.
3. ```cd``` to the root directory of the prepared project distribution.
4. Install the core Sun lab development dependencies into the ***base*** mamba environment via the 
   ```mamba install tox uv tox-uv``` command.
5. Use the ```tox -e create``` command to create the project-specific development environment followed by 
   ```tox -e install``` command to install the project into that environment as a library.

### Additional Dependencies

In addition to installing the project and all user dependencies, install the following dependencies:

1. [Python](https://www.python.org/downloads/) distributions, one for each version supported by the developed project. 
   Currently, this library supports the three latest stable versions. It is recommended to use a tool like 
   [pyenv](https://github.com/pyenv/pyenv) to install and manage the required versions.

### Development Automation

This project comes with a fully configured set of automation pipelines implemented using 
[tox](https://tox.wiki/en/latest/user_guide.html). Check the [tox.ini file](tox.ini) for details about the 
available pipelines and their implementation. Alternatively, call ```tox list``` from the root directory of the project
to see the list of available tasks.

**Note!** All pull requests for this project have to successfully complete the ```tox``` task before being merged. 
To expedite the task’s runtime, use the ```tox --parallel``` command to run some tasks in-parallel.

### Automation Troubleshooting

Many packages used in 'tox' automation pipelines (uv, mypy, ruff) and 'tox' itself may experience runtime failures. In 
most cases, this is related to their caching behavior. If an unintelligible error is encountered with 
any of the automation components, deleting the corresponding .cache (.tox, .ruff_cache, .mypy_cache, etc.) manually 
or via a CLI command typically solves the issue.

___

## Versioning

This project uses [semantic versioning](https://semver.org/). See the 
[tags on this repository](https://github.com/Sun-Lab-NBB/ataraxis-base-utilities/tags) for the available project 
releases.

---

## Authors

- Ivan Kondratyev ([Inkaros](https://github.com/Inkaros))

___

## License

This project is licensed under the GPL3 License: see the [LICENSE](LICENSE) file for details.

___

## Acknowledgments

- All Sun lab [members](https://neuroai.github.io/sunlab/people) for providing the inspiration and comments during the
  development of this library.
- The creators of all other dependencies and projects listed in the [pyproject.toml](pyproject.toml) file.

---
