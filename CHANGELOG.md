# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Git-Tag-Based Semversioning Implementation
- **Complete git-tag-based semantic versioning system**
  - Automated version management from git tags
  - Support for pre-release versions (alpha, beta, rc)
  - Version validation and increment logic
- **Comprehensive test suite with 90%+ coverage**
  - Unit tests for all PathConfig classes
  - Integration tests for end-to-end functionality
  - Cross-platform compatibility tests
  - Configuration loading and validation tests
  - Property-based testing for path validation
  - Mock tests for OS-specific behavior
- **Command-line interface with rich formatting**
  - Complete CLI implementation in `src/twat_os/__main__.py`
  - Rich tables and colored output
  - Commands: `paths`, `get`, `create`, `clean`, `info`, `version`
  - Support for package-specific and custom configurations
- **Build automation scripts**
  - `scripts/build.py` - Package building and distribution
  - `scripts/test.py` - Comprehensive test execution
  - `scripts/release.py` - Release management and git tagging
  - `scripts/check.py` - Pre-commit quality checks
- **Enhanced GitHub Actions CI/CD pipeline**
  - Multi-platform testing (Linux, macOS, Windows)
  - Multi-version Python support (3.10, 3.11, 3.12)
  - Security scanning with Bandit and Safety
  - Type checking with MyPy
  - Coverage reporting and aggregation
  - Standalone binary builds with PyInstaller
  - Automated PyPI publishing on git tags
- **Development environment automation**
  - Installation script (`install.sh`) for quick setup
  - Makefile with common development commands
  - Virtual environment management with uv
  - Pre-commit hooks configuration
- **Comprehensive documentation**
  - `DEVELOPMENT.md` - Complete development guide
  - `PLAN.md` - Detailed implementation plan
  - Updated `README.md` with new features
  - In-code documentation improvements

### Enhanced
- **GitHub Actions workflows**
  - Multi-OS testing matrix for better compatibility
  - Security scanning integration
  - Enhanced release workflow with binary builds
  - Automated changelog generation
  - Coverage reporting and artifact management
- **Package configuration**
  - Added missing dependencies (tomli, rich)
  - Enhanced development dependencies
  - Improved optional dependency groups
  - Better build system configuration
- **Code quality and testing**
  - Comprehensive linting with Ruff
  - Type checking with MyPy
  - Security scanning with Bandit and Safety
  - Coverage reporting with pytest-cov
  - Multi-platform and multi-version testing

### Fixed
- **Missing CLI implementation**
  - Implemented complete `__main__.py` module
  - Added Fire and Rich dependencies
  - Created comprehensive CLI commands
- **Package metadata and dependencies**
  - Added missing core dependencies
  - Fixed import issues
  - Improved version handling
- **Cross-platform compatibility**
  - Enhanced path handling for Windows, macOS, Linux
  - Fixed environment variable expansion
  - Improved directory creation logic
- **Configuration loading**
  - Better error handling for missing configs
  - Improved TOML parsing
  - Enhanced validation and edge case handling

### Infrastructure
- **Automated release pipeline**
  - Git tag validation
  - Multi-platform binary builds
  - PyPI publishing automation
  - GitHub release creation
- **Quality assurance**
  - Pre-commit hooks
  - Continuous integration
  - Security scanning
  - Dependency management
- **Development tools**
  - Build automation
  - Test execution
  - Release management
  - Code quality checks

### Previous Changes
- Created `TODO.md`, `LOG.md`, and `CHANGELOG.md`
- Corrected project description in `.cursor/rules/0project.mdc` to accurately describe `twat-os`
- Simplified `cleanup.py` to use system `repomix` command
- Improved `src/twat_os/paths.py` with better typing and parameter handling
- Updated `pyproject.toml` with core dependencies and improved configuration
- Resolved Ruff and MyPy issues in codebase
