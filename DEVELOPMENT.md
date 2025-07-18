# Development Guide for twat-os

This guide provides instructions for developing, testing, and releasing the twat-os package.

## Quick Start

### Prerequisites

- Python 3.10 or later
- Git
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation

#### Option 1: Using the install script (recommended)

```bash
./install.sh
```

#### Option 2: Manual installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv --python 3.12

# Activate virtual environment
source .venv/bin/activate

# Install in development mode
uv pip install -e ".[dev,test]"
```

## Development Workflow

### Scripts

The project includes several Python scripts in the `scripts/` directory for common tasks:

#### Building

```bash
# Build the package
uv run python scripts/build.py all

# Just build (no clean)
uv run python scripts/build.py build

# Clean build artifacts
uv run python scripts/build.py clean
```

#### Testing

```bash
# Run all tests
uv run python scripts/test.py all

# Run specific test types
uv run python scripts/test.py unit
uv run python scripts/test.py integration
uv run python scripts/test.py platform

# Run quick tests (no coverage)
uv run python scripts/test.py quick

# Run with coverage report
uv run python scripts/test.py coverage-report
```

#### Quality Checks

```bash
# Run all checks
uv run python scripts/check.py all

# Run specific checks
uv run python scripts/check.py lint
uv run python scripts/check.py typecheck
uv run python scripts/check.py security

# Auto-fix issues
uv run python scripts/check.py fix
```

#### Releases

```bash
# Check release readiness
uv run python scripts/release.py check

# Create release
uv run python scripts/release.py patch     # 1.0.0 -> 1.0.1
uv run python scripts/release.py minor     # 1.0.0 -> 1.1.0
uv run python scripts/release.py major     # 1.0.0 -> 2.0.0

# Custom version
uv run python scripts/release.py release --version v1.2.3

# Dry run
uv run python scripts/release.py patch --dry-run
```

### Using Makefile

Alternatively, you can use the Makefile for common tasks:

```bash
# Install development dependencies
make dev-install

# Run tests
make test

# Build package
make build

# Run all checks
make all

# Clean artifacts
make clean
```

## Testing

### Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_package.py          # Basic package tests
├── test_config_loading.py   # Configuration loading tests
├── test_cross_platform.py   # Cross-platform compatibility tests
├── unit/                    # Unit tests
│   ├── test_path_config.py  # PathConfig class tests
│   └── test_path_manager.py # PathManager class tests
└── integration/             # Integration tests
    └── test_path_integration.py
```

### Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest --cov=src/twat_os --cov-report=html tests/

# Run specific test files
uv run pytest tests/unit/test_path_manager.py -v

# Run tests matching a pattern
uv run pytest -k "test_path" tests/

# Run tests in parallel
uv run pytest -n auto tests/
```

## Git Tag-Based Semversioning

The project uses git tags for versioning following semantic versioning:

### Version Format

- **Release**: `v1.0.0`, `v1.2.3`
- **Pre-release**: `v1.0.0-alpha.1`, `v1.0.0-beta.2`, `v1.0.0-rc.1`

### Creating Releases

1. **Ensure clean state**: All tests pass, no uncommitted changes
2. **Create tag**: Use the release script or manual git commands
3. **Push tag**: GitHub Actions will automatically build and release

```bash
# Using release script (recommended)
uv run python scripts/release.py patch

# Manual git commands
git tag v1.0.1
git push origin v1.0.1
```

## GitHub Actions

The project includes comprehensive GitHub Actions workflows:

### CI Pipeline (`.github/workflows/push.yml`)

- **Quality checks**: Linting, formatting, type checking, security
- **Multi-platform testing**: Ubuntu, Windows, macOS
- **Multi-version testing**: Python 3.10, 3.11, 3.12
- **Build verification**: Package building and distribution checks
- **Coverage reporting**: Combined coverage reports

### Release Pipeline (`.github/workflows/release.yml`)

- **Release validation**: Tag format, tests, quality checks
- **Multi-platform builds**: Python packages and standalone binaries
- **PyPI publishing**: Automated package publishing
- **GitHub releases**: Automated release creation with artifacts

## Building Binaries

The project supports building standalone binaries using PyInstaller:

```bash
# Install PyInstaller
uv pip install pyinstaller

# Build binary
uv run pyinstaller --onefile --name=twat-os --console src/twat_os/__main__.py

# Test binary
./dist/twat-os version
```

## CLI Usage

The package includes a command-line interface:

```bash
# Install and use
pip install twat-os

# Show all paths
twat-os paths

# Get specific path
twat-os get cache base_dir

# Show version
twat-os version

# Show help
twat-os --help
```

## Code Quality

### Linting and Formatting

- **Ruff**: Linting and formatting
- **MyPy**: Type checking
- **Bandit**: Security linting
- **Safety**: Dependency security

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Code Style

- **Line length**: 88 characters
- **Import organization**: Absolute imports, isort compliance
- **Type hints**: Required for all public APIs
- **Docstrings**: Google style docstrings

## Project Structure

```
twat-os/
├── src/twat_os/           # Main package code
│   ├── __init__.py
│   ├── __main__.py        # CLI entry point
│   ├── paths.py           # Core path management
│   └── paths.toml         # Default configuration
├── tests/                 # Test suite
├── scripts/               # Development scripts
├── .github/workflows/     # GitHub Actions
├── pyproject.toml         # Project configuration
├── Makefile               # Development shortcuts
└── install.sh             # Installation script
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure package is installed in development mode
2. **Test failures**: Check Python version compatibility
3. **Build failures**: Verify all dependencies are installed
4. **Permission errors**: Use virtual environment

### Getting Help

1. Check the documentation in `README.md`
2. Review test examples in `tests/`
3. Use the development scripts with `--help`
4. Open an issue on GitHub

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run all tests and checks
5. Submit a pull request

### Pull Request Checklist

- [ ] Tests pass on all platforms
- [ ] Code is properly formatted
- [ ] Type checking passes
- [ ] Security checks pass
- [ ] Documentation is updated
- [ ] Changelog entry is added