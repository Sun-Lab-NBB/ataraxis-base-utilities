# ataraxis-base-utilities

Python library that provides a minimalistic set of shared utility functions used to support most other Sun Lab projects.

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
- Frequently re-implemented utility method, such as a method that ensures the parent directory of a file path exists.
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
2. ```cd``` to the root directory of the project using your command line interface of choice.
3. Run ```python -m pip install .``` to install the project. Alternatively, if using a distribution with precompiled
   binaries, use ```python -m pip install WHEEL_PATH```, replacing 'WHEEL_PATH' with the path to the wheel file.

### PIP

Use the following command to install the library using PIP: ```pip install ataraxis-base-utilities```
___

## Usage
This section is broken into subsections for each exposed utility class or module. For each, it progresses from a 
minimalistic example and / or 'quickstart' to detailed notes on nuanced class functionality 
(if the class has such functionality).

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
of each method, so the text should look good regardless of the backend used. In the case that you want to use console
as a formatter, rather than a message processor, you can use Console.format_message() method:
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
By default, console starts 'disabled.' You can enable or disable it at any time! When using console to add functionality
to libraries, do not enable() the console. This way, you both add console functionality to your library and allow the 
end-user to decide how much output they want to see and in what format.
```
from ataraxis_base_utilities import console, LogLevel

# Most basically, the console can be enabled() or disabled() any time using the appropriate methods:
console.enable()
console.disable()

# To check the current console status, you can use the getter method:
assert not console.is_enabled
```

#### Configuring console: output control
By default, console is configured to print information and error messages to the terminal. However, you can 
flexibly set what kind of messages it processes and where they go. To do so, you can use the extensive set of setter and
getter methods.
```
from ataraxis_base_utilities import console, LogLevel
console.enable()

# Consider debug message printing, which is disabled by default:
console.echo('Debug', level=LogLevel.DEBUG)

# If we enable debug printing, the message will show up in terminal as expected:
console.set_debug_terminal(True)
console.echo('Debug', level=LogLevel.DEBUG)

# To verify if a particular output format for a message type is enabled, you can use the getter method:
assert console.debug_terminal
assert not console.error_file

# The class allows you to flexibly configure terminal-printing and file-logging for Debug-, Info to Warning and Error+
# messages. The default 'console' configuration can be obtained by using the following setter methods and arguments:
console.set_debug_terminal(False)
console.set_debug_file(False)
console.set_message_terminal(True)
console.set_message_file(False)
console.set_error_terminal(True)
console.set_error_file(False)

# Note, 'getter' properties are named identical to setter methods, minus the 'set_' part:
assert not console.debug_terminal
assert not console.debug_file
assert console.message_terminal
assert not console.message_file
assert console.error_terminal
assert not console.error_file
```

#### Configuring console: log paths
For a message to be written to a log file, it is not enough to just 'enable' that output type. Additionally, you need 
to provide console with a path to the log file to write to and, if it does not exist, create. This is done through a 
separate set of setter and getter methods:
```
from ataraxis_base_utilities import console, LogExtensions
from pathlib import Path

# By default, the console is not provided with a path to the message log file and does not support writing messages to
# log file.
assert console.message_log_path is None

# You can provide it with a custom log file to enable logging functionality:
example_path = f"example{LogExtensions.LOG}"
console.set_message_log_path(Path(example_path))
assert console.message_log_path == Path(example_path)

# Note that the class supports only a set of file-extensions. For your convenience, they are available from
# LogExtensions class:
log_file = Path(f"example{LogExtensions.LOG}")
text_file = Path(f"example{LogExtensions.TXT}")
json_file = Path(f"example{LogExtensions.JSON}")

# As with other class configuration attributes, you can flexibly configure log files for each of the supported message
# groups:
console.set_message_log_path(log_file)
console.set_debug_log_path(text_file)
console.set_error_log_path(json_file)

# You can retrieve the used log file path at any time using an appropriate getter property:
log_file = console.message_log_path
text_file = console.debug_log_path
json_file = console.error_log_path
```

#### Configuring console: error runtime control
Console.error() significantly expands your ability to control how errors are handled. Specifically, its behavior can 
range from generating default Python tracebacks to redirecting errors to log files to executing custom error callback
functions. Note, most of this functionality is only supported by our default 'loguru' backend.
```
from ataraxis_base_utilities import console, default_callback
console.enable()

# By default, the console is configured to call sys.exit() as a callback to prevent providing two error traces: one from
# loguru and the other from Python. To prevent this behavior, set console callback to None:
console.set_callback(None)

# This prints the error to terminal, but does not abort runtime.
try:
    console.error("Test error", RuntimeError)
except RuntimeError:
    print("You will not see this.")

# By default, console will not re-raise the logged error as a Python error.
assert not console.reraise

# However, if your use case needs this functionality, you can always enable it:
console.set_reraise(True)

try:
    console.error("Test error", ValueError)
except ValueError:
    print("The error was re-raised as expected.")


# WARNING! Callbacks, when provided, are executed before re-raising the error. If callback calls runtime-breaking
# functions, such as sys.exit(), it will interfere with error re-raising.
def benign_callback():
    print('I do not cause a runtime error.')


console.set_callback(benign_callback)
try:
    console.error("Test error", TypeError)
except TypeError:
    print("Benign callback did not interfere with raising the error.")

# Default callback will, however, clash with 'reraise' functionality:
console.set_callback(default_callback)
try:
    # This will abort the runtime through 'default_callback' calling sys.exit().
    console.error("Test error", KeyError)
except KeyError:
    print("This will not be displayed.")
```

#### Custom Console instances:
While this class is designed ot be used through the 'console' variable, you can also instantiate and use a custom 
Console class instance. Unlike 'console' variable, this class will not be shared across all modules and libraries, 
potentially allowing to isolate its configuration from the rest of your project. Note, since 'LOGURU' backend uses the 
shared 'logger,' instantiating a new CConsole class does not automatically guarantee isolation!
```
from ataraxis_base_utilities import Console, LogBackends, LogExtensions

# The most important advantage of using the custom console is the ability to specify the backend other than the default
# 'LOGURU' backend. # All supported backends are available through the LogBackends enumeration.
click_console = Console(logger_backend=LogBackends.CLICK)

# Additionally, you can customize the formatting applied to messages:
format_console = Console(line_width=200, break_long_words=True, break_on_hyphens=True, use_color=False)

# Finally, you can make console safer by overriding the 'auto_handles' attribute to prevent 'LOGURU' consoles from 
# automatically editing the shared 'logger' instance handles. To learn more about handles, see 'add_handles()' section.
loguru_console = Console(logger_backend=LogBackends.LOGURU, auto_handles=False)


# All attributes discussed in previous sections can be set by initialization arguments to the Console class:
def custom_callback():
    """Custom callback function"""
    pass


debug_log_path = f"debug{LogExtensions.LOG}"

example_console = Console(
        logger_backend=LogBackends.LOGURU,
        debug_log_path=debug_log_path,
        message_log_path=None,
        error_log_path=None,
        line_width=120,
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
        reraise_errors=True
    )
```

#### Loguru Console: add_handles()
This section only applies to Console using 'loguru' backend, which includes the default 'console' variable. Loguru 
relies on its 'logger' variable to be provided with handles that determine how to process messages. Similarly, Console
comes with add_handles() method that can be called to replace active handles with console-specific handles. Note, since
'logger' is shared across all libraries and modules, editing handles can interfere with any other class that uses 
logger. Default console is written with the assumption that nothing else uses logger and, by default, removes all active
handles before adding its custom handles before adding its custom handles. Not only this, but it also calls 
add_handles() automatically when initialized or when any of its attributes are edited.
```
from ataraxis_base_utilities import Console, LogBackends, LogExtensions

# By default, uses loguru backend
console = Console(auto_handles=False)
console.enable()

# Consoles that are not initialized with auto_handles=True require manually calling add_handles() method before calling
# echo() or error() methods.
console.add_handles(remove_existing_handles=False)  # This call will NOT remove default handles

# This should produce two messages: one using the default 'console' variable handle that replaced 'logger' handle and
# another using the custom handle we added with add_handles() call.
console.echo("Hello, World!")

# To reset all handles, we cna use the default add_handles() argument:
console.add_handles()
console.echo("Now there is only one")

# Another important feature only available through 'add_handles' is the ability to 'enqueue' messages. This helps with
# using console from multiple processes by passing all messages through a shared processing queue.
console.add_handles(enqueue=True)
console.echo("The API remains the same though!")
```

#### Additional notes on usage:
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

### Standalone Methods
The standalone methods are a broad collection of utility functions that either abstract away the boilerplate code for 
common data manipulations or provide novel functionality not commonly available through popular Python libraries used 
by our projects. Generally, these methods are straightforward to use and do not require detailed explanation:

#### Ensure list

As the name implies, this method ensures that the input is a Python list. If the input is not a Python list, the method
converts it into a list. If conversion fails, the method raises a ValueError.

```
import numpy as np
from ataraxis_base_utilities import ensure_list

# Ensures and, if necessary, converts inputs to the Python list type:
out_list = ensure_list(input_item=(1, 2, 3, 4))
assert isinstance(out_list, list)
assert out_list == [1, 2, 3, 4]

# It works for a wide range of inputs numpy arrays...
numpy_array = np.array([1, 2, 3, 4])
out_list = ensure_list(input_item=numpy_array)
assert isinstance(out_list, list)
assert out_list == [1, 2, 3, 4]

# And scalars
out_list = ensure_list(input_item=1)
assert isinstance(out_list, list)
assert out_list == [1]
```

#### Compare nested tuples
This method is designed to compliment numpy 'array_equal' method to provide a way of comparing two-dimensional (nested)
tuples. The method allows comparing Python tuple with multiple element datatypes and uneven sub-tuple topologies: the 
functionality that is not present in the array_equal() method.

```
from ataraxis_base_utilities import compare_nested_tuples

# The method works for different sub-tuple shapes and element datatypes
tuple_1 = (1, 2, ("text", True))
tuple_2 = (1, 2, ("text", True))
assert compare_nested_tuples(x=tuple_1, y=tuple_2)

# The method takes element datatype into consideration when comparing tuples!
tuple_2 = (1, '2', ("text", True))
assert not compare_nested_tuples(x=tuple_1, y=tuple_2)
```

#### Chunk iterable
This method converts input iterables into chunks of the requested size. Primarily, this is helpful when load-balancing 
data for parallel processing and similar operations.
```

import numpy as np
from ataraxis_base_utilities import chunk_iterable

# Note, while the method tries to produce equally sized chunks, the final chunk may contain fewer items if the input
# iterable is not evenly divisible by chunk size. The method returns a Generator that can be used to yield chunks:
x = [1, 2, 3, 4, 5, 6, 7]
chunk_generator = chunk_iterable(iterable=x, chunk_size=2)

expected_chunks = ((1, 2), (3, 4), (5, 6), (7,))
for num, chunk in enumerate(chunk_generator):
    assert expected_chunks[num] == chunk

# The method works for both python iterables and one-dimensional numpy arrays. For numpy inputs, it returns numpy
# arrays as outputs:
numpy_x = np.array(x)
chunk_generator = chunk_iterable(iterable=numpy_x, chunk_size=3)

expected_chunks = (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7]))
for num, chunk in enumerate(chunk_generator):
    assert np.array_equal(expected_chunks[num], chunk)
```

#### Check condition
This method provides a generalized logic comparison interface that functions similar to using the logical operators, 
such as '==' directly. The main purpose of this method is to provide an interface that behaves similarly regardless of 
input. This is useful in cases such as verifying the output of a function that can return multiple different datatypes.

```
import numpy as np
from ataraxis_base_utilities import check_condition

# The method can be considered a wrapper around common logical operators used for value comparison:
assert check_condition(checked_value=3, condition_value=3, condition_operator='==')
assert check_condition(checked_value='One', condition_value='Two', condition_operator='!=')

# However, it abstracts away working with different types of inputs, such as numpy arrays:
output = check_condition(checked_value=np.array([1, 2, 3]), condition_value=1, condition_operator='==')
assert np.array_equal(output, np.array([True, False, False]))

# And python iterables:
output = check_condition(checked_value=[1, 1, 1], condition_value=1, condition_operator='==')
assert np.array_equal(output, [True, True, True])
```

#### Ensure directory exists
This method was originally defined as private method for the Console class, but it is now a public standalone method. 
This method checks whether the directory portion of the input path exists and, if not, it creates the necessary 
directory hierarchy. This is helpful when working with files, as files cannot be created if their root directory does
not exist.
```
import tempfile
from pathlib import Path
from ataraxis_base_utilities import ensure_directory_exists

# Precreates a temporary directory
with tempfile.TemporaryDirectory() as temp_dir:

    # Defines a file-path that adds two subdirectories and defines a text file
    file_path = Path(f"{temp_dir}/subfolder1/subfolder2/my_file.txt")

    # Ensures that the first subfolder does not exist
    assert not Path(f"{temp_dir}/subfolder1").exists()

    # This ensures that the subdirectories exist
    ensure_directory_exists(path=file_path)

    # Ensures that both subfolders now exist
    assert Path(f"{temp_dir}/subfolder1").exists()
    assert Path(f"{temp_dir}/subfolder1/subfolder2").exists()

    # The method does nothing if the directories already exist.
    ensure_directory_exists(path=file_path)

    # The method does not create files, it only created directories.
    assert not file_path.exists()
```
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
       [environments](#environments) section for other environment installation methods.
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
The environment snapshots were taken on each of the three explicitly supported OS families: Windows 11, OSx (M1) 15.1
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
- [loguru](https://github.com/Delgan/loguru) and [click](https://github.com/pallets/click/) projects for providing
  all low-level functionality for the Console class.
- [numpy](https://github.com/numpy/numpy) project for providing low-level functionality for some of the 
  standalone methods.
- The creators of all other projects used in our development automation pipelines [see pyproject.toml](pyproject.toml).

---
