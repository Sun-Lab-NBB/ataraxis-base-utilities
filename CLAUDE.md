# Claude Code Instructions

## Session start behavior

At the beginning of each coding session, before making any code changes, you should build a comprehensive understanding
of the codebase by invoking the `/explore-codebase` skill.

This ensures you:
- Understand the project architecture before modifying code
- Follow existing patterns and conventions
- Do not introduce inconsistencies or break integrations

## Style guide compliance

You MUST invoke the appropriate style skill before performing ANY of the following tasks:

| Task                                | Skill to invoke    |
|-------------------------------------|--------------------|
| Writing or modifying Python code    | `/python-style`    |
| Writing or modifying README files   | `/readme-style`    |
| Writing git commit messages         | `/commit`          |
| Writing or modifying skill files    | `/skill-design`    |
| Writing or modifying pyproject.toml | `/pyproject-style` |
| Writing or modifying tox.ini        | `/tox-config`      |
| Writing or modifying API docs       | `/api-docs`        |

Each skill contains a verification checklist that you MUST complete before submitting any work. Failure to invoke the
appropriate skill results in style violations.

## Cross-referenced library verification

Sun Lab projects often depend on other `ataraxis-*` or `sl-*` libraries. These libraries may be stored locally in the
same parent directory as this project (`/home/cyberaxolotl/Desktop/GitHubRepos/`).

**Before writing code that interacts with a cross-referenced library, you MUST:**

1. **Check for local version**: Look for the library in the parent directory (e.g., `../ataraxis-time/`,
   `../ataraxis-data-structures/`).

2. **Compare versions**: If a local copy exists, compare its version against the latest release or main branch on
   GitHub:
   - Read the local `pyproject.toml` to get the current version
   - Use `gh api repos/Sun-Lab-NBB/{repo-name}/releases/latest` to check the latest release
   - Alternatively, check the main branch version on GitHub

3. **Handle version mismatches**: If the local version differs from the latest release or main branch, notify the user
   with the following options:
   - **Use online version**: Fetch documentation and API details from the GitHub repository
   - **Update local copy**: The user will pull the latest changes locally before proceeding

4. **Proceed with correct source**: Use whichever version the user selects as the authoritative reference for API
   usage, patterns, and documentation.

**Why this matters**: Skills and documentation may reference outdated APIs. Always verify against the actual library
state to prevent integration errors.

## Available skills

| Skill                | Description                                                               |
|----------------------|---------------------------------------------------------------------------|
| `/explore-codebase`  | Perform in-depth codebase exploration at session start                    |
| `/python-style`      | Apply Sun Lab Python coding conventions (REQUIRED for all Python changes) |
| `/readme-style`      | Apply Sun Lab README conventions (REQUIRED for README changes)            |
| `/commit`            | Draft Sun Lab style-compliant git commit messages                         |
| `/skill-design`      | Generate and verify skill files and CLAUDE.md project instructions        |
| `/pyproject-style`   | Apply Sun Lab pyproject.toml conventions                                  |
| `/tox-config`        | Apply Sun Lab tox.ini conventions                                         |
| `/api-docs`          | Apply Sun Lab API documentation conventions                               |

## Downstream library integration

This library is a dependency for virtually all other `ataraxis-*` and `sl-*` libraries in the Sun Lab ecosystem.
Changes to the public API affect all downstream projects. You MUST maintain backwards compatibility when modifying
exported classes, functions, or constants unless the user explicitly requests a breaking change.

## Project context

This is **ataraxis-base-utilities**, a foundational Python library that provides unified message handling, error
management, and common utility functions for all Sun Lab projects at Cornell University.

### Key areas

| Directory                                         | Purpose                                    |
|---------------------------------------------------|--------------------------------------------|
| `src/ataraxis_base_utilities/`                    | Main library source code                   |
| `src/ataraxis_base_utilities/console/`            | Console class for unified message handling |
| `src/ataraxis_base_utilities/standalone_methods/` | Common utility functions                   |
| `tests/`                                          | Test suite                                 |
| `docs/`                                           | Sphinx documentation source                |

### Architecture

- **Console module**: The core `Console` class wraps loguru to provide a unified message and error handling framework.
  The global `console` instance is pre-configured and shared across all Sun Lab projects. Includes `ProgressBar` for
  tqdm-based progress tracking, `LogLevel` and `LogFormats` enumerations, and a `temporarily_enabled()` context
  manager.
- **Standalone methods**: Utility functions for list conversion (`ensure_list`), iterable chunking
  (`chunk_iterable`), error formatting (`error_format`), CPU core resolution (`resolve_worker_count`,
  `resolve_parallel_job_capacity`), and NumPy byte serialization (`convert_scalar_to_bytes`,
  `convert_bytes_to_scalar`, `convert_array_to_bytes`, `convert_bytes_to_array`).
- **No CLI**: This is a library-only project with no command-line entry points.
- **Singleton pattern**: The global `console` instance allows consistent configuration from application entry points.

### Core components

| Component                       | File                                       | Purpose                                      |
|---------------------------------|--------------------------------------------|----------------------------------------------|
| `Console`                       | `console/console_class.py`                 | Unified terminal printing and file logging   |
| `LogLevel`                      | `console/console_class.py`                 | Enum for log levels (DEBUG through CRITICAL) |
| `LogFormats`                    | `console/console_class.py`                 | Enum for log file formats (LOG, TXT, JSON)   |
| `ProgressBar`                   | `console/console_class.py`                 | Wrapper for tqdm progress bars               |
| `ensure_directory_exists`       | `console/console_class.py`                 | Creates directories if they do not exist     |
| `ensure_list`                   | `standalone_methods/standalone_methods.py` | Converts various types to lists              |
| `chunk_iterable`                | `standalone_methods/standalone_methods.py` | Splits iterables into sized chunks           |
| `error_format`                  | `standalone_methods/standalone_methods.py` | Formats messages for test exception matching |
| `resolve_worker_count`          | `standalone_methods/standalone_methods.py` | Determines CPU core allocation for jobs      |
| `resolve_parallel_job_capacity` | `standalone_methods/standalone_methods.py` | Determines parallel job count from cores     |
| `convert_scalar_to_bytes`       | `standalone_methods/standalone_methods.py` | Serializes scalars to uint8 byte arrays      |
| `convert_bytes_to_scalar`       | `standalone_methods/standalone_methods.py` | Deserializes uint8 byte arrays to scalars    |
| `convert_array_to_bytes`        | `standalone_methods/standalone_methods.py` | Serializes NumPy arrays to uint8 bytes       |
| `convert_bytes_to_array`        | `standalone_methods/standalone_methods.py` | Deserializes uint8 bytes to typed arrays     |

### Code standards

- MyPy strict mode with full type annotations
- Google-style docstrings
- 120 character line limit
- See `/python-style` for complete conventions

### Workflow guidance

**Modifying the Console class:**

1. Review `src/ataraxis_base_utilities/console/console_class.py` for current implementation
2. Understand the loguru integration and three-tier logging (debug, message, error)
3. Maintain backwards compatibility — this library is used by all other Sun Lab projects
4. Test changes thoroughly as they affect the entire ecosystem

**Adding utility functions:**

1. Review existing functions in `src/ataraxis_base_utilities/standalone_methods/standalone_methods.py`
2. Follow the same patterns for type hints, docstrings, and error handling
3. Export new functions in `src/ataraxis_base_utilities/__init__.py`
4. Add corresponding tests in `tests/standalone_methods/`

**Important considerations:**

- This library intentionally conflicts with other loguru-using libraries
- The global `console` instance must be enabled from application entry points
- Use `console.error()` instead of `raise` for all error handling within this library
