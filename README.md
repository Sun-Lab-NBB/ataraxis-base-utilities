# ataraxis-base-utilities

A Python library that provides a minimalistic set of shared utility functions used to support most other Sun Lab 
projects.

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

This library is one of the two 'base' dependency libraries used by every other Sun Lab project (the other being 
[ataraxis-automation](https://github.com/Sun-Lab-NBB/ataraxis-automation)). It aggregates shared utility 
functions, such as message and error logging, reused across all other Sun lab projects.

___

## Features

- Supports Windows, Linux, and macOS.
- Provides a unified approach to message and error formatting, printing, and logging through the Console class.
- Pure-python API.
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

For users, all library dependencies are installed automatically for all supported installation methods 
(see the [Installation](#installation) section). For developers, see the [Developers](#developers) section for 
information on installing additional development dependencies.

___

## Installation

### Source

1. Download this repository to the local machine using the preferred method, such as git-cloning. Use one of the stable 
   releases that include precompiled binary and source code distribution (sdist) wheels.
2. ```cd``` to the root directory of the project.
3. Run ```python -m pip install .``` to install the project. Alternatively, if using a distribution with precompiled
   binaries, use ```python -m pip install WHEEL_PATH```, replacing 'WHEEL_PATH' with the path to the wheel file.

### pip

Use the following command to install the library using pip: ```pip install ataraxis-base-utilities```.

___

## Usage


### Console
The Console class provides message and error display (via terminal) and logging (to files) functionality. Primarily, 
this is realized through the [loguru](https://github.com/Delgan/loguru) backend. It is highly advised to check loguru 
documentation to understand how Console functions under-the-hood, although this is not strictly required. As a secondary
backend, the class uses [click](https://click.palletsprojects.com/en/8.1.x/), so it may be beneficial to review its 
documentation if loguru backend is not appropriate for your specific use case.

#### Quickstart
Most class functionality revolves around 2 methods: ```echo()``` and ```error()```. To make adoption as frictionless
as possible, we offer a preconfigured class instance exposed through 'console' class variable that can be used 'as-is'
and shared between multiple modules:
```
from ataraxis_base_utilities import console

# The class is disabled by default, so it needs to be enabled to see method outputs. You do not need to have it enabled
# to add error() or echo() calls to your code though.
console.enable()

# Use this instead of print()!
console.echo("This is essentially a better 'print'.")

# Use this instead of 'raise Exception'!
console.error("This is essentially a better 'raise'.")
```

#### Echo
Console.echo() method can be thought of as a better print() with some additional functionality. For example, you can
provide the desired message 'level' to finely control how it will be processed:
```
from ataraxis_base_utilities import console, LogLevel
console.enable()

# By default, console is configured to NOT print debug messages. You will not see anything after this call
console.echo(message='Debug', level=LogLevel.DEBUG)

# But you will see this information message
console.echo(message='Info', level=LogLevel.INFO)

# Or this error message
console.echo(message='Error', level=LogLevel.ERROR)

# Disabled console will not print any messages at all.
console.disable()
status = console.echo(message='Info', level=LogLevel.INFO)

# To help you track if console is not printing due to being disabled, it returns 'False' when you call echo() while the
# class is disabled.
assert status is False

# However, if lack of printing is due to how console is configured and not it being disabled, the status will be set to
# 'True'.
console.enable()
status = console.echo(message='Debug', level=LogLevel.DEBUG)
assert status
```

#### Error
Console.error() method can be thought of as a more nuanced 'raise Exception' directive. Most of the additional 
functionality of this method comes from Console class configuration, and in its most basic form, this is just a
wrapper around 'raise':
```
from ataraxis_base_utilities import console
console.enable()

# By default, console uses 'default callback' to abort the active runtime after raising an error. Since this will
# interrupt this example, this needs to be disabled. See 'error runtime control' section for more details.
console.set_callback(None)

# You can specify the exception to be raised by providing it as an 'error' argument. By default, this argument is
# set to RuntimeError.
console.error(message="TypeError", error=TypeError)


# This works for custom exceptions as well!
class CustomError(Exception):
    pass


console.error(message="CustomError", error=CustomError)


# When console is disabled, error() behaves identically to 'raise' directive. This way, your errors will always be
# raised, regardless of whether console is enabled or not.
console.disable()
console.error(message="ValueError", error=ValueError)
```

#### Format Message
All console methods format input messages to fit the default width-limit of 120 characters. This was chosen as it is 
both likely to fit into any modern terminal and gives us a little more space than the default legacy '80' limit used by
many projects. The formatting takes into consideration that 'loguru' backend adds some ID information to the beginning 
of each method, so the text should look good regardless of the backend used. In the case that you want to use the 
console as a formatter, rather than a message processor, you can use the Console.format_message() method:
```
from ataraxis_base_utilities import console

# Let's use this test message
message = (
    "This is a very long message that exceeds our default limit of 120 characters. As such, it needs to be wrapped to "
    "appear correctly when printed to terminal (or saved to a log file)."
)

# This shows how the message looks without formatting
print(message)

# This formats the message according to our standards. Note how this works regardless of whether console is enabled or 
# not!
formatted_message = console.format_message(message)

# See how it compares to the original message!
print(formatted_message)
```

#### Configuring console: enable / disable
By default, the console starts 'disabled.' You can enable or disable it at any time! When using console to add 
functionality to libraries, do not enable() the console. This way, you both add console functionality to your library 
and allow the end-user to decide how much output they want to see and in what format.
```
from ataraxis_base_utilities import console, LogLevel

# Most basically, the console can be enabled() or disabled() any time using the appropriate methods:
console.enable()
console.disable()

# To check the current console status, you can use the getter method:
assert not console.is_enabled
```

#### Additional notes on usage:
Generally, Console class is designed to be used across many libraries that may also be dependent on each other. 
Therefore, it should be used similar to how it is advised to use Loguru for logging: when using Console in a library, 
do not call add_handles() or enable() methods. The only exception to this rule is when running in interactive mode 
(cli, benchmark, script) that is known to be the highest hierarchy (nothing else imports your code, it imports 
everything else).

To facilitate correct usage, the library exposes the 'console' variable preconfigured to use Loguru backend and is 
not enabled by default. You can use this variable to add Console-backed printing and logging functionality to your 
library. Whenever your library is imported, the end-user can then enable() and add_handles() using the same 'console'
variable, which will automatically work for all console-based statements across all libraries. This way, the exact 
configuration is left up to the end-user, but your code will still raise errors and can be debugged using custom 
logging configurations.

### Standalone Methods
The standalone methods are a broad collection of utility functions that either abstract away the boilerplate code for 
common data manipulations or provide novel functionality not commonly available through popular Python libraries used 
by our projects. Generally, these methods are straightforward to use and do not require detailed explanation:

___

## API Documentation

See the [API documentation](https://ataraxis-base-utilities-api-docs.netlify.app/) for the detailed description of the 
methods and classes exposed by components of this library.

___

## Developers

This section provides installation, dependency, and build-system instructions for the developers that want to
modify the source code of this library. Additionally, it contains instructions for recreating the conda environments
that were used during development from the included .yml files.

### Installing the library

1. Download this repository to your local machine using your preferred method, such as git-cloning.
2. ```cd``` to the root directory of the project using your command line interface of choice.
3. Install development dependencies. You have multiple options of satisfying this requirement:
    1. **_Preferred Method:_** Use conda or pip to install
       [tox](https://tox.wiki/en/latest/user_guide.html) or use an environment that has it installed and
       call ```tox -e import``` to automatically import the os-specific development environment included with the
       source code in your local conda distribution. Alternatively, you can use ```tox -e create``` to create the 
       environment from scratch and automatically install the necessary dependencies using pyproject.toml file. See 
       the [environments](#environments) section for other environment installation methods.
    2. Run ```python -m pip install .'[dev]'``` command to install development dependencies and the library using 
       pip. On some systems, you may need to use a slightly modified version of this command: 
       ```python -m pip install .[dev]```.
    3. As long as you have an environment with [tox](https://tox.wiki/en/latest/user_guide.html) installed
       and do not intend to run any code outside the predefined project automation pipelines, tox will automatically
       install all required dependencies for each task.

**Note:** When using tox automation, having a local version of the library may interfere with tox tasks that attempt
to build the library using an isolated environment. While the problem is rare, our 'tox' pipelines automatically 
install and uninstall the project from its' conda environment. This relies on a static tox configuration and will only 
target the project-specific environment, so it is advised to always ```tox -e import``` or ```tox -e create``` the 
project environment using 'tox' before running other tox commands.

### Additional Dependencies

In addition to installing the required python packages, separately install the following dependencies:

1. [Python](https://www.python.org/downloads/) distributions, one for each version that you intend to support. 
  Currently, this library supports version 3.10 and above. The easiest way to get tox to work as intended is to have 
  separate python distributions, but using [pyenv](https://github.com/pyenv/pyenv) is a good alternative too. 
  This is needed for the 'test' task to work as intended.

### Development Automation

This project comes with a fully configured set of automation pipelines implemented using 
[tox](https://tox.wiki/en/latest/user_guide.html). Check [tox.ini file](tox.ini) for details about 
available pipelines and their implementation. Alternatively, call ```tox list``` from the root directory of the project
to see the list of available tasks.

**Note!** All commits to this project have to successfully complete the ```tox``` task before being pushed to GitHub. 
To minimize the runtime task for this task, use ```tox --parallel```.

For more information, you can also see the 'Usage' section of the 
[ataraxis-automation project](https://github.com/Sun-Lab-NBB/ataraxis-automation) documentation.

### Environments

All environments used during development are exported as .yml files and as spec.txt files to the [envs](envs) folder.
The environment snapshots were taken on each of the three explicitly supported OS families: Windows 11, OSx (M1) 15.1,
and Linux Ubuntu 24.04 LTS.

**Note!** Since the OSx environment was built for an M1 (Apple Silicon) platform, it may not work on Intel-based 
Apple devices.

To install the development environment for your OS:

1. Download this repository to your local machine using your preferred method, such as git-cloning.
2. ```cd``` into the [envs](envs) folder.
3. Use one of the installation methods below:
    1. **_Preferred Method_**: Install [tox](https://tox.wiki/en/latest/user_guide.html) or use another
       environment with already installed tox and call ```tox -e import```.
    2. **_Alternative Method_**: Run ```conda env create -f ENVNAME.yml``` or ```mamba env create -f ENVNAME.yml```. 
       Replace 'ENVNAME.yml' with the name of the environment you want to install (axbu_dev_osx for OSx, 
       axbu_dev_win for Windows, and axbu_dev_lin for Linux).

**Hint:** while only the platforms mentioned above were explicitly evaluated, this project is likely to work on any 
common OS, but may require additional configurations steps.

Since the release of [ataraxis-automation](https://github.com/Sun-Lab-NBB/ataraxis-automation) version 2.0.0 you can 
also create the development environment from scratch via pyproject.toml dependencies. To do this, use 
```tox -e create``` from project root directory.

### Automation Troubleshooting

Many packages used in 'tox' automation pipelines (uv, mypy, ruff) and 'tox' itself are prone to various failures. In 
most cases, this is related to their caching behavior. Despite a considerable effort to disable caching behavior known 
to be problematic, in some cases it cannot or should not be eliminated. If you run into an unintelligible error with 
any of the automation components, deleting the corresponding .cache (.tox, .ruff_cache, .mypy_cache, etc.) manually 
or via a cli command is very likely to fix the issue.

___

## Versioning

This project uses [semantic versioning](https://semver.org/). For the versions available, see the 
[tags on this repository](https://github.com/Sun-Lab-NBB/ataraxis-base-utilities/tags).

---

## Authors

- Ivan Kondratyev ([Inkaros](https://github.com/Inkaros))
- 
___

## License

This project is licensed under the GPL3 License: see the [LICENSE](LICENSE) file for details.

___

## Acknowledgments

- All Sun Lab [members](https://neuroai.github.io/sunlab/people) for providing the inspiration and comments during the
  development of this library.
- The creators of all other dependencies and projects listed in the [pyproject.toml](pyproject.toml) file.

---
