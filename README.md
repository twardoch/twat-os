# twat-os: OS-Aware Path Management for the "twat" Ecosystem

**`twat-os` is a Python library designed for developers working within the "twat" ecosystem. It provides a robust and standardized way to manage operating system-specific file system paths for your applications and plugins.**

If you're building tools, plugins, or any software that integrates with or extends the "twat" framework, `twat-os` helps you handle where your application should store cache files, configuration, user data, logs, temporary files, and even specialized data like "GenAI" models or LoRAs. It ensures your application behaves correctly and consistently across different operating systems (like Windows, macOS, and Linux) by using platform-appropriate directories.

## Key Features

*   **OS-Agnostic Paths**: Uses `platformdirs` internally to determine standard locations for user-specific data (cache, config, data, etc.) on any major OS.
*   **Package-Specific Organization**: Easily create and manage paths that are namespaced to your specific "twat" package or plugin.
*   **Configurable**: Default path templates are provided, but can be overridden with a custom TOML configuration file.
*   **Automatic Directory Creation**: Directories are created automatically when paths are requested, simplifying file operations.
*   **GenAI Path Management**: Includes pre-defined configurations for common Generative AI related paths (models, LoRAs, outputs).
*   **`twat` Plugin**: Seamlessly integrates as an `os` plugin within the broader "twat" framework.
*   **Modern Python**: Developed with Python 3.10+, type hints, and standard tooling.

## Who is this for?

`twat-os` is for Python developers who are:

*   Building applications or plugins for the "twat" framework.
*   Need a reliable way to manage file storage locations.
*   Want their software to follow best practices for file system organization on different operating systems.

## Why is it useful?

*   **Standardization**: Ensures all "twat" ecosystem components can find and store files in predictable locations.
*   **Cross-Platform Compatibility**: Write your path logic once, and trust it works correctly everywhere.
*   **Ease of Use**: Simplifies common tasks like finding a user's cache directory or creating a dedicated space for your package's data.
*   **Reduces Boilerplate**: No need to write custom OS-detection and path-joining logic for every project.

## Installation

`twat-os` requires Python 3.10 or later. You can install it using pip:

```bash
pip install twat-os
```

## Usage

`twat-os` can be used programmatically as a Python library. It also registers itself as a plugin within the "twat" framework and defines a command-line interface (CLI) entry point.

### Programmatic Usage (as a Library)

The primary way to use `twat-os` is by interacting with the `PathManager` class found in `twat_os.paths`.

```python
from twat_os.paths import PathManager

# 1. Get a PathManager instance, typically for your specific package
# This helps in creating package-specific subdirectories.
pm = PathManager.for_package("my_awesome_twat_plugin")

# 2. Access various path categories:
# All paths are pathlib.Path objects.

# Cache paths
user_cache_dir = pm.cache.base_dir  # General twat cache: ~/.cache/twat (example)
plugin_cache_dir = pm.cache.package_dir # Package-specific: ~/.cache/twat/my_awesome_twat_plugin (example)

# Configuration paths
user_config_dir = pm.config_dir.base_dir    # General twat config: ~/.config/twat (example)
plugin_config_dir = pm.config_dir.package_dir # Package-specific: ~/.config/twat/my_awesome_twat_plugin (example)

# Data paths
user_data_dir = pm.data.base_dir        # General twat data: ~/.local/share/twat (example)
plugin_data_dir = pm.data.package_dir     # Package-specific: ~/.local/share/twat/my_awesome_twat_plugin (example)

# Log paths
user_log_dir = pm.logs.base_dir         # General twat logs: ~/.local/state/twat/logs (example)
plugin_log_dir = pm.logs.package_dir      # Package-specific: ~/.local/state/twat/logs/my_awesome_twat_plugin (example)

# Temporary paths
user_temp_dir = pm.temp.base_dir        # General twat temp: /tmp/twat (example, actual varies)
plugin_temp_dir = pm.temp.package_dir     # Package-specific: /tmp/twat/my_awesome_twat_plugin (example)

# GenAI specific paths (these are typically shared, not package-specific by default configuration)
genai_lora_dir = pm.genai.lora_dir      # ~/.local/share/twat/genai/loras (example)
genai_model_dir = pm.genai.model_dir    # ~/.local/share/twat/genai/models (example)
genai_output_dir = pm.genai.output_dir  # ~/Pictures/twat_genai (example)

# Using the generic get_path() method:
# plugin_cache_alt = pm.get_path("cache", "package_dir")
# genai_models_alt = pm.get_path("genai", "model_dir")

print(f"Store cache for my plugin at: {plugin_cache_dir}")
# plugin_cache_dir.mkdir(parents=True, exist_ok=True) # PathManager usually does this for you if create_dirs is True

# If you don't need package-specific paths, you can instantiate PathManager directly:
# generic_pm = PathManager()
# general_twat_cache = generic_pm.cache.base_dir
```

By default, `PathManager` will attempt to create these directories if they do not already exist (controlled by the `create_dirs` parameter, which is `True` by default). The example paths like `~/.cache/twat` are illustrative; actual paths are determined by `platformdirs`.

### As a `twat` Plugin

`twat-os` is registered as an `os` plugin when installed in an environment with the `twat` core package (due to the `[project.entry-points."twat.plugins"] os = "twat_os"` line in `pyproject.toml`). This means its functionalities might be accessible via the `twat` plugin system.

For example (hypothetical usage, consult `twat` documentation):
```python
# import twat
#
# path_manager_instance = twat.plugins.os.get_path_manager() # Or similar API
# cache_dir = twat.plugins.os.get_cache_dir("my_plugin")
```
The exact mechanism for accessing plugins can vary based on the `twat` framework's design. Please refer to the `twat` core documentation for details on using plugins.

### Command-Line Interface (CLI)

`twat-os` defines a command-line tool named `twat-os`, intended to be invoked as:
```bash
twat-os --help
```

**Important Note**: While the `twat-os` CLI entry point (`twat_os.__main__:main`) is defined in the `pyproject.toml`, the corresponding `src/twat_os/__main__.py` file that implements its functionality appears to be missing from the source distribution as of its current version. This suggests the CLI might be unimplemented or non-functional at present. Please check the project's issue tracker or future releases for updates on CLI capabilities.

---

## Technical Details

This section dives deeper into how `twat-os` works internally, its core components, and configuration options.

### Core Components

*   **`PathManager` (`twat_os.paths.PathManager`)**:
    *   This is the central class you'll interact with.
    *   It can be instantiated directly (`PathManager()`) for general "twat" paths or, more commonly, using the class method `PathManager.for_package("your_package_name")` to get paths namespaced for your specific package.
    *   It accepts an optional `config_file` argument (path to a TOML file) to load custom path configurations. If not provided, it loads defaults from the `paths.toml` file co-located with `paths.py`.
    *   It also takes a `create_dirs: bool` argument (defaults to `True`) which controls whether it automatically creates directories when path properties are accessed.

*   **`PathConfig` and its Subclasses**:
    *   `twat_os.paths` defines several Pydantic models that inherit from `PathConfig`:
        *   `CacheConfig`: For cache directories.
        *   `ConfigDirConfig`: For configuration file directories.
        *   `DataDirConfig`: For persistent user data directories.
        *   `TempDirConfig`: For temporary runtime file directories.
        *   `GenAIConfig`: For paths related to Generative AI, such as LoRAs, models, and image outputs. This has more specialized attributes like `lora_dir`, `model_dir`, and `output_dir`.
        *   `LogConfig`: For log file directories.
    *   Each of these models defines a `base_dir` (the main directory for that category, e.g., `~/.cache/twat`) and potentially a `package_dir` template (e.g., `~/.cache/twat/{package_name}`).
    *   These Pydantic models handle path expansion (user home `~`, environment variables like `${HOME}`) and validation.

*   **`paths.toml`**:
    *   This TOML file, located within the `twat_os` package (`src/twat_os/paths.toml`), stores the default path templates.
    *   It's organized into sections corresponding to the `PathConfig` subclasses (e.g., `[cache]`, `[config]`, `[genai]`).
    *   Example snippet from `paths.toml`:
        ```toml
        [cache]
        # Base directory for all cache operations
        base_dir = "~/.cache/twat"
        # Directory for storing package-specific cache data
        package_dir = "~/.cache/twat/{package_name}"

        [genai]
        # Directory for storing LoRA files
        lora_dir = "~/.local/share/twat/genai/loras"
        # Directory for model weights
        model_dir = "~/.local/share/twat/genai/models"
        ```

*   **`platformdirs` Integration**:
    *   `twat-os` uses the `platformdirs` library to determine the appropriate, OS-agnostic locations for user-specific directories. For example, `platformdirs.user_cache_dir()` might return `~/.cache` on Linux, `~/Library/Caches` on macOS, and `C:\\Users\\<user>\\AppData\\Local` on Windows.
    *   The default values in `paths.toml` often leverage these by appending a "twat" subdirectory (e.g., `Path(platformdirs.user_cache_dir()) / "twat"`).

### Path Resolution and Structure

*   **Base Directories (`base_dir`)**: For each category (cache, config, etc.), `PathManager` provides access to a base directory. This is typically a general directory for all "twat" related files of that type (e.g., `pm.cache.base_dir` points to the main `twat` cache folder).
*   **Package-Specific Directories (`package_dir`)**: When `PathManager` is instantiated using `PathManager.for_package("my_package")`, the `package_dir` attribute of each category config will point to a subdirectory specific to `"my_package"` within the corresponding `base_dir` (e.g., `pm.config_dir.package_dir` might be `~/.config/twat/my_package`). This is achieved by formatting the `package_dir` string from `paths.toml` with the provided `package_name`.
*   **`GenAIConfig` Paths**: The `GenAIConfig` (`pm.genai`) is slightly different as its attributes (`lora_dir`, `model_dir`, `output_dir`) often point to shared locations rather than package-specific subdirectories by default, reflecting common usage patterns for these resources.
*   **Directory Creation**: If `create_if_missing` is `True` (the default) on the `PathManager` instance, accessing a path property (e.g., `pm.cache.package_dir`) will automatically ensure that the directory (and any necessary parent directories) exists.

### Configuration

*   **Default Configuration**: The default path templates are loaded from `src/twat_os/paths.toml` within the installed `twat_os` package.
*   **Custom Configuration File**: You can override these defaults by providing a path to your own TOML file when creating a `PathManager` instance:
    ```python
    from twat_os.paths import PathManager

    # custom_paths.toml could look like:
    # [cache]
    # base_dir = "/mnt/fast_storage/twat_cache"
    # package_dir = "/mnt/fast_storage/twat_cache/{package_name}"

    pm = PathManager(package_name="my_plugin", config_file="path/to/your/custom_paths.toml")
    # print(pm.cache.package_dir) # Output would be /mnt/fast_storage/twat_cache/my_plugin (if my_plugin was the package_name)
    ```
    Your custom TOML file only needs to include the sections and keys you wish to override. Unspecified paths will still use the defaults.

### Extensibility

Currently, `twat-os` is designed with a fixed set of path categories (cache, config, data, temp, genai, logs). Adding new top-level path categories would require modifying the library's source code, specifically by:

1.  Adding a new `PathConfig` subclass in `paths.py`.
2.  Adding a corresponding section and default values to `paths.toml`.
3.  Adding an attribute to `PathManager` to hold an instance of your new config class and initializing it in `PathManager._init_paths()`.

For most use cases, the existing categories should suffice. If you need custom subdirectories within an existing category for your package, you can easily achieve this by appending to the paths provided by `PathManager`:

```python
# Assuming pm = PathManager.for_package("my_package")
my_package_custom_data = pm.data.package_dir / "my_special_subdirectory"
my_package_custom_data.mkdir(parents=True, exist_ok=True) # Standard pathlib usage
```

---

## Development & Contributing

This project uses [Hatch](https://hatch.pypa.io/) for managing the development environment, dependencies, and common tasks like testing, linting, and building. The configuration for Hatch can be found in `pyproject.toml`.

### Setting up a Development Environment

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/twardoch/twat-os.git
    cd twat-os
    ```

2.  **Install Hatch:**
    If you don't have Hatch, install it, for example, via pipx or pip:
    ```bash
    pipx install hatch # Recommended
    # or
    # pip install hatch
    ```

3.  **Activate the development environment:**
    This command creates an isolated virtual environment using Hatch, installs all dependencies (including development tools), and makes the `twat-os` package available in editable mode.
    ```bash
    hatch shell
    ```
    You are now in the project's virtual environment, ready to run development commands.

### Common Development Tasks

All commands below are run from within the Hatch-activated shell (i.e., after running `hatch shell`). Refer to `tool.hatch.envs.default.scripts` and `tool.hatch.envs.lint.scripts` in `pyproject.toml` for the full list of available scripts.

*   **Run Tests:**
    ```bash
    hatch run test
    # or specifically: hatch run default.test
    ```
    This executes the test suite using `pytest`.

*   **Run Tests with Coverage:**
    ```bash
    hatch run test-cov
    # or specifically: hatch run default.test-cov
    ```
    This runs tests and generates a coverage report to the terminal.

*   **Type Checking:**
    `twat-os` uses `Mypy` for static type checking.
    ```bash
    hatch run type-check
    # or specifically: hatch run default.type-check
    # For more specific Mypy commands, see the 'lint' environment:
    # hatch run lint:typing
    ```

*   **Linting and Formatting:**
    The project uses `Ruff` for both linting and code formatting to ensure consistency.
    *   To check for linting issues and formatting:
        ```bash
        hatch run lint
        # or specifically: hatch run default.lint
        # To check style only (without Mypy):
        # hatch run lint:style
        ```
    *   To automatically fix linting issues and format code:
        ```bash
        hatch run fix
        # or specifically: hatch run default.fix
        # For formatting only (without fixing lint issues that aren't auto-fixable by format):
        # hatch run lint:fmt
        ```

*   **Pre-commit Hooks:**
    This project uses pre-commit hooks defined in `.pre-commit-config.yaml` to automatically check and format code before committing. It's highly recommended to install them in your local clone:
    ```bash
    pre-commit install
    ```
    This will ensure that your contributions adhere to the project's coding standards by running checks automatically when you `git commit`.

### Coding Standards

*   **Python Version:** Code should be compatible with Python 3.10 and newer (as specified in `pyproject.toml`).
*   **Type Hinting:** All new code should include comprehensive type hints. `Mypy` is used to enforce this.
*   **Code Style:** Follow the `Ruff` formatting guidelines (which are largely PEP 8 compliant, with a line length of 88 characters, configured in `pyproject.toml`). Running `hatch run fix` or `hatch run lint:fmt` will format your code correctly.
*   **Imports:** Imports should be organized according to `isort` rules (handled by `Ruff`). Relative imports within the `src/twat_os` package are banned; use absolute imports (e.g., `from twat_os.paths import ...`).

### Contributing

Contributions are welcome! Here's how you can help:

1.  **Reporting Bugs:**
    *   If you find a bug, please open an issue on the [GitHub Issues page](https://github.com/twardoch/twat-os/issues).
    *   Include as much detail as possible: steps to reproduce, expected behavior, actual behavior, your environment (OS, Python version, `twat-os` version).

2.  **Suggesting Enhancements:**
    *   Open an issue to discuss your ideas for new features or improvements before starting significant work. This helps ensure alignment with the project's goals.

3.  **Pull Requests:**
    *   Fork the repository on GitHub.
    *   Create a new branch for your feature or bug fix from the `main` branch: `git checkout -b feature/my-new-feature` or `git checkout -b fix/issue-123`.
    *   Make your changes.
    *   Ensure all tests pass (`hatch run test`).
    *   Ensure your code is fully typed and passes linting (`hatch run type-check`, `hatch run lint`).
    *   Add tests for any new functionality or bug fixes. Aim for high test coverage.
    *   Update documentation (including this README, or other docs if they exist) if you change behavior, add features, or update CLI options.
    *   Commit your changes with clear, descriptive commit messages.
    *   Push your branch to your fork on GitHub.
    *   Open a pull request against the `main` branch of the `twardoch/twat-os` repository. Provide a clear description of your changes in the PR.

### Understanding the Plugin Nature

Remember that `twat-os` also functions as a plugin for the wider "twat" ecosystem (registered via `[project.entry-points."twat.plugins"]`). Changes should ideally maintain compatibility and consider how they might affect users relying on this plugin integration.

### License

By contributing, you agree that your contributions will be licensed under the MIT License that covers the project. See the `LICENSE` file for details.