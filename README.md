# ataraxis-base-utilities

Python library that provides a minimalistic set of shared utility functions used to support most other Sun Lab projects.

![PyPI - Version](https://img.shields.io/pypi/v/ataraxis-base-utilities)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ataraxis-base-utilities)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](ht1tps://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![type-checked: mypy](https://img.shields.io/badge/type--checked-mypy-blue?style=flat-square&logo=python)
![PyPI - License](https://img.shields.io/pypi/l/ataraxis-base-utilities)
![PyPI - Status](https://img.shields.io/pypi/status/ataraxis-base-utilities)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/ataraxis-base-utilities)
___

## Detailed Description

This library is one of the two 'base' dependency libraries used by every other Sun Lab project (the other being 
[ataraxis-automation](https://github.com/Sun-Lab-NBB/ataraxis-automation)). It aggregates common utility functions 
that are expected to be shared and reused by many other lab projects, such as message and error logging. This library is
designed to avoid re-implementing the same set of utility features for every lab project. This is important, since most
of our codebases employ a highly modular and decentralized design with many independent subprojects dynamically 
assembled into functional pipelines. Generally, any class or function copied with minor modifications into five 
or more Sun Lab projects is a good candidate for inclusion into this library.

Despite a strong focus on supporting Sun Lab projects, this library can be used in non-lab projects with minor 
refactoring. Specifically, anyone willing to reuse this library in their project may need to adjust the default values
and configurations used throughout this library to match their specific needs. Otherwise, it should be readily 
integrable with any other project due to its minimalistic design (both in terms of features and dependencies).
___

## Features

- Supports Windows, Linux, and OSx.
- Loguru-based Console class that provides message and logging functionality.
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
(see [Installation](#installation) section). For developers, see the [Developers](#developers) section for 
information on installing additional development dependencies.
___

## Installation

### Source

1. Download this repository to your local machine using your preferred method, such as git-cloning. Optionally, use one
   of the stable releases that include precompiled binary wheels in addition to source code.
2. ```cd``` to the root directory of the project using your CLI of choice.
3. Run ```python -m pip install .``` to install the project. Alternatively, if using a distribution with precompiled
   binaries, use ```python -m pip install WHEEL_PATH```, replacing 'WHEEL_PATH' with the path to the wheel file.

### PIP

Use the following command to install the library using PIP: ```pip install ataraxis-base-utilities```

### Conda / Mamba

**_Note. Due to conda-forge contributing process being more nuanced than pip uploads, conda versions may lag behind
pip and source code distributions._**

Use the following command to install the library using Conda or Mamba: ```conda install ataraxis-base-utilities```
___

## Usage

### Console
The Console class provides message and error display (via terminal) and logging (to files) functionality. Primarily, 
this is realized through the [loguru](https://github.com/Delgan/loguru) backend. It is highly advised checking loguru 
documentation to understand how Console functions under-the-hood, although this is not strictly required. As a secondary
backend, the class uses [click](https://click.palletsprojects.com/en/8.1.x/), so it may be beneficial to review its 
documentation if loguru backend is not appropriate for your specific use case.

This is a minimal example of how to use the class, assuming you want to use default parameters:
```
# Import 'console' and helper classes
from ataraxis_base_utilities import console, LogLevel, LogExtensions
from pathlib import Path

# 'console' is a global variable that functions similar to Loguru 'logger'. It is ready to be used right after import.

# When imported, console is DISABLED. It will not print anything and will raise errors just like python does.

# These two methods configure (add handles) to the console and enable it to print and log text and error messages.
# To understand the purpose of 'add_handles()' step, review 'loguru' documentation and the API / source code for the 
# Console class. Generally, it configures 'sinks' that determine how 'echo()' and 'error()' generated messages are 
# processed by the loguru backend.
console.add_handles()
console.enable()

# This functions just like 'print' does. This sends the message using 'Info' log level. See Loguru documentation for 
# details on log levels.
console.echo('Message to Print')

# This functions just like 'raise RuntimeError()' does. Use this in place of typical exceptions to allow logging them 
# when console is enabled.
console.error('Error message')

# This shows how you can chose what error is raised.
console.error('Error message', error=ValueError)

# By default, console variable is not configured to save messages and errors to log files. To add log file support, 
# follow these steps:

# First, provide it with valid log file path:
extension = LogExtensions.LOG
message_log = Path(f"my_log{extension}")
console.set_message_log_path(message_log)

# Then reconfigure the console to allow logging messages. Any subsequent console echo() call will both print the 
# message to the terminal and log it to the log file.
console.add_handles(message_file=True)
```

This is a more detailed example that also showcases some of the configuration parameters used by Console methods and 
de novo class instantiation:
```
# First, import the console class from the library. It also helps to include helper enumerations.
from ataraxis_base_utilities import Console, LogBackends, LogLevel

# Configure Console to write messages to files in addition to terminals.
debug_log: str = "debug.json"
error_log_path: str = "error.txt"
message_log_path: str = "message.log"
file_console: Console = Console(
    debug_log_path=debug_log, error_log_path=error_log_path, message_log_path=message_log_path
)

# Add handles (Only for LOGURU backend). Make sure file handles are enabled.
file_console.add_handles(remove_existing_handles=True, debug_file=True, message_file=True, error_file=True)

# Next, the console has to be enabled. By default, it is disabled and does not process any echo() or error() calls.
file_console.enable()

# Attempts to print debug message, which will go to file, but not terminal (terminal handle for debug was not added).
message: str = "Hi there! I am debug."
file_console.echo(message=message, level=LogLevel.DEBUG, terminal=True, log=True)

# Prints to terminal only, warnings is at the 'message' level.
message = "Hi there! I am warning."
file_console.echo(message=message, level=LogLevel.WARNING, terminal=True, log=False)

# Raises an error, logs it, but does not break runtime.
message = "Oh no! I am error."
file_console.error(message=message, error=ValueError, callback=None, reraise=False, terminal=True, log=True)

# Disabling the console allows calling methods, but they do nothing.
file_console.disable()

message = "Too bad you will never see me!"
# echo returns False when console is disabled, so you can always check what is going on if you do not see anything!
assert not file_console.echo(message=message, level=LogLevel.ERROR, terminal=True, log=False)

# Click is available as an alternative backend.
click_console = Console(logger_backend=LogBackends.CLICK)

# Click does not use handles, so console just needs to be enabled.
click_console.enable()

# Echo works very similar to loguru, but log levels do not do much.
message = "I may not be much, but I am honest work!"
click_console.echo(message, log=False)

# Not super important, but you can also just format strings using format_message().
message = ("This is a very long message. So long in fact, that it exceeds the default line limit of Console class. "
           "format_message() will automatically wrap the message as needed to fit into the width-limit.")
print(click_console.format_message(message=message, loguru=False))

# Also, click does not support callback functionality for errors or detailed traceback, like loguru does, so it is
# often better to log and reraise any errors when using click.
message = "I may be excessive, but so what?"
click_console.error(message, ValueError, reraise=True, terminal=True, log=False)
```

### Additional notes on usage:
Generally, Console class is designed to be used across many libraries that may also be dependent on each other. 
Therefore, it should be used similar to how it is advised to use Loguru for logging: when using Console in a library, 
do not call add_handles() or enable() methods. The only exception to this rule is when running in interactive mode 
(cli, benchmark, script) that is known to be the highest hierarchy (nothing else imports your code, it imports 
everything else).

To facilitate correct usage, the library exposes 'console' variable preconfigured to use Loguru backend and is 
not enabled by default. You can use this variable to add Console-backed printing and logging functionality to your 
library. Whenever your library is imported, the end-user can then enable() and add_handles() using the same 'console'
variable, which will automatically work for all console-based statements across all libraries. This way, the exact 
configuration is left up to end-user, but your code will still raise errors and can be debugged using custom 
logging configurations.
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
2. ```cd``` to the root directory of the project using your CLI of choice.
3. Install development dependencies. You have multiple options of satisfying this requirement:
    1. **_Preferred Method:_** Use conda or pip to install
       [tox](https://tox.wiki/en/latest/config.html#provision_tox_env) or use an environment that has it installed and
       call ```tox -e import``` to automatically import the os-specific development environment included with the
       source code in your local conda distribution. Alternatively, you can use ```tox -e create``` to create the 
       environment from scratch and automatically install the necessary dependencies using pyproject.toml file. See 
       [environments](#environments) section for other environment installation methods.
    2. Run ```python -m pip install .'[dev]'``` command to install development dependencies and the library using 
       pip. On some systems, you may need to use a slightly modified version of this command: 
       ```python -m pip install .[dev]```.
    3. As long as you have an environment with [tox](https://tox.wiki/en/latest/config.html#provision_tox_env) installed
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
[tox](https://tox.wiki/en/latest/config.html#provision_tox_env). Check [tox.ini file](tox.ini) for details about 
available pipelines and their implementation. Alternatively, call ```tox list``` from the root directory of the project
to see the list of available tasks.

Also, it may be beneficial to check the documentation for the 
[ataraxis-automation](https://github.com/Sun-Lab-NBB/ataraxis-automation) library. This library provides low-level 
scripts used by different 'tox' tasks. Importantly, all conda environment manipulations are realized through scripts 
offered by our automation library. The documentation for the library includes additional information on all available 
'tox' tasks and general notes on writing custom tox.ini files to work with our automation scripts.

**Note!** All commits to this project have to successfully complete the ```tox``` task before being pushed to GitHub. 
To minimize the runtime task for this task, use ```tox --parallel```.

### Environments

All environments used during development are exported as .yml files and as spec.txt files to the [envs](envs) folder.
The environment snapshots were taken on each of the three explicitly supported OS families: Windows 11, OSx (M1) 14.5
and Linux Ubuntu 22.04 LTS.

**Note!** Since the OSx environment was built against an M1 (Apple Silicon) platform and may not work on Intel-based 
Apple devices.

To install the development environment for your OS:

1. Download this repository to your local machine using your preferred method, such as git-cloning.
2. ```cd``` into the [envs](envs) folder.
3. Use one of the installation methods below:
    1. **_Preferred Method_**: Install [tox](https://tox.wiki/en/latest/config.html#provision_tox_env) or use another
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

We use [semantic versioning](https://semver.org/) for this project. For the versions available, see the 
[tags on this repository](https://github.com/Sun-Lab-NBB/ataraxis-base-utilities/tags).
---

## Authors

- Ivan Kondratyev ([Inkaros](https://github.com/Inkaros))
___

## License

This project is licensed under the GPL3 License: see the [LICENSE](LICENSE) file for details.
___

## Acknowledgments

- All Sun Lab [members](https://neuroai.github.io/sunlab/people) for providing the inspiration and comments during the
  development of this library.
