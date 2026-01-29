# Claude Code Instructions

## Session Start Behavior

At the beginning of each coding session, before making any code changes, you should build a comprehensive
understanding of the codebase by invoking the `/explore-codebase` skill.

This ensures you:
- Understand the project architecture before modifying code
- Follow existing patterns and conventions
- Don't introduce inconsistencies or break integrations

## Style Guide Requirements

You MUST invoke `/sun-lab-style` and read the appropriate guide before performing ANY of the following tasks:

| Task                              | Guide to Read      |
|-----------------------------------|--------------------|
| Writing or modifying Python code  | PYTHON_STYLE.md    |
| Writing or modifying README files | README_STYLE.md    |
| Writing git commit messages       | COMMIT_STYLE.md    |
| Writing or modifying skill files  | SKILL_STYLE.md     |

This is non-negotiable. The skill contains verification checklists that you MUST complete before submitting any work.
Failure to read the appropriate guide results in style violations.

## Cross-Referenced Library Verification

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

## Available Skills

| Skill               | Description                                                      |
|---------------------|------------------------------------------------------------------|
| `/explore-codebase` | Perform in-depth codebase exploration at session start           |
| `/sun-lab-style`    | Apply Sun Lab coding conventions (REQUIRED for all code changes) |

## Project Context

This is **ataraxis-base-utilities**, a foundational Python library that provides unified message handling, error
management, and common utility functions for all Sun Lab projects at Cornell University. This library is a dependency
for virtually all other `ataraxis-*` and `sl-*` libraries in the Sun Lab ecosystem.

### Key Areas

| Directory                                             | Purpose                                      |
|-------------------------------------------------------|----------------------------------------------|
| `src/ataraxis_base_utilities/`                        | Main library source code                     |
| `src/ataraxis_base_utilities/console/`                | Console class for unified message handling   |
| `src/ataraxis_base_utilities/standalone_methods/`     | Common utility functions                     |
| `tests/`                                              | Test suite                                   |
| `docs/`                                               | Sphinx documentation source                  |

### Architecture

- **Console Module**: The core `Console` class wraps loguru to provide a unified message/error handling framework.
  The global `console` instance is pre-configured and shared across all Sun Lab projects.
- **Standalone Methods**: Utility functions like `ensure_list()`, `chunk_iterable()`, and `error_format()` for common
  data manipulation tasks.
- **No CLI**: This is a library-only project with no command-line entry points.
- **Singleton Pattern**: The global `console` instance allows consistent configuration from application entry points.

### Core Components

| Component               | File                                       | Purpose                                          |
|-------------------------|--------------------------------------------|--------------------------------------------------|
| Console                 | `console/console_class.py`                 | Unified terminal printing and file logging       |
| LogLevel                | `console/console_class.py`                 | Enum for log levels (DEBUG, INFO, SUCCESS, etc.) |
| LogFormats              | `console/console_class.py`                 | Enum for log file formats (LOG, TXT, JSON)       |
| ensure_list             | `standalone_methods/standalone_methods.py` | Converts various types to lists                  |
| chunk_iterable          | `standalone_methods/standalone_methods.py` | Splits iterables into chunks                     |
| error_format            | `standalone_methods/standalone_methods.py` | Formats messages for test exception matching     |
| ensure_directory_exists | `console/console_class.py`                 | Creates directories if they don't exist          |

### Code Standards

- MyPy strict mode with full type annotations
- Google-style docstrings
- 120 character line limit
- See `/sun-lab-style` for complete conventions

### Workflow Guidance

**Modifying the Console class:**

1. Review `src/ataraxis_base_utilities/console/console_class.py` for current implementation
2. Understand the loguru integration and three-tier logging (debug, message, error)
3. Maintain backwards compatibility - this library is used by all other Sun Lab projects
4. Test changes thoroughly as they affect the entire ecosystem

**Adding utility functions:**

1. Review existing functions in `src/ataraxis_base_utilities/standalone_methods/standalone_methods.py`
2. Follow the same patterns for type hints, docstrings, and error handling
3. Export new functions in `src/ataraxis_base_utilities/__init__.py`
4. Add corresponding tests in `tests/standalone_methods/`

**Important considerations:**

- This library intentionally conflicts with other loguru-using libraries
- Changes to the public API affect all downstream Sun Lab projects
- The global `console` instance must be enabled from application entry points
- Use `console.error()` instead of `raise` for all error handling within this library
