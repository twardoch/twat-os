# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Created `TODO.md`, `LOG.md`, and `CHANGELOG.md`.

### Changed
- Corrected project description in `.cursor/rules/0project.mdc` to accurately describe `twat-os`.

### Refactored
- Simplified `cleanup.py`:
    - Removed internal `repomix` function.
    - Modified the script to call the system `repomix` command and output to `llms.txt` instead of `REPO_CONTENT.txt`.
- Improved `src/twat_os/paths.py`:
    - Added `from typing_extensions import Self` for compatibility.
    - Changed `create_dirs` parameter in `PathManager.__init__` to be keyword-only, resolving Ruff FBT001/FBT002 warnings.
- Updated `pyproject.toml`:
    - Added `pydantic` and `platformdirs` to core project dependencies.
    - Added `typing-extensions` to `dev` dependencies.
    - Removed the `[project.optional-dependencies.all]` group.
    - Updated `tool.hatch.envs.default.features` to exclude `all`.

### Fixed
- Resolved Ruff and MyPy issues identified during validation:
    - `src/twat_os/paths.py`:
        - Changed `os.path.expanduser()` to `Path().expanduser()` (PTH111).
        - Removed redundant `cast` in `get_path()` method.
        - Ruff automatically removed unused `typing.cast` import.
    - `tests/test_package.py`:
        - Moved `import twat_os` to top-level (PLC0415).
        - Added `-> None` return type hint to `test_version()`.
