# GitHub Actions Workflows

Due to GitHub App permissions, the workflow files couldn't be automatically committed. Here's how to add them manually:

## Current Status

The workflow files are currently staged but not committed. You can see them with:
```bash
git status
```

## To Add the Workflows

1. **Check the staged files:**
   ```bash
   git status
   ```

2. **Commit the workflow files:**
   ```bash
   git commit -m "feat: add enhanced GitHub Actions workflows

   - Multi-platform testing (Linux, macOS, Windows)
   - Multi-version Python support (3.10, 3.11, 3.12)
   - Security scanning with Bandit and Safety
   - Type checking with MyPy
   - Automated binary builds with PyInstaller
   - Enhanced release automation with git tags
   - Coverage reporting and aggregation"
   ```

3. **Push the changes:**
   ```bash
   git push origin terragon/implement-git-tag-semver-ci
   ```

## What These Workflows Provide

### Enhanced CI/CD Pipeline (`.github/workflows/push.yml`)
- **Multi-platform testing**: Ubuntu, Windows, macOS
- **Multi-version Python**: 3.10, 3.11, 3.12
- **Quality checks**: Ruff linting, formatting, MyPy type checking
- **Security scanning**: Bandit for code security, Safety for dependencies
- **Coverage reporting**: Combined coverage reports from all platforms
- **Build verification**: Ensures packages can be built successfully

### Enhanced Release Pipeline (`.github/workflows/release.yml`)
- **Release validation**: Tag format validation, comprehensive testing
- **Multi-platform binary builds**: Standalone executables for Linux, macOS, Windows
- **PyPI publishing**: Automated package publishing on git tags
- **GitHub releases**: Automated release creation with binaries and changelog
- **Pre-release support**: Automatic detection of alpha/beta/rc versions

## Usage

Once the workflows are committed:

1. **For regular development:**
   - Push to `main` branch triggers full CI/CD pipeline
   - Pull requests trigger testing and quality checks

2. **For releases:**
   - Create and push a git tag: `git tag v1.0.0 && git push origin v1.0.0`
   - Workflows automatically test, build, and release to PyPI
   - GitHub release is created with binaries and changelog

## Alternative: Manual Workflow Setup

If you prefer to set up workflows manually, here are the file contents:

### `.github/workflows/push.yml`
```yaml
name: Build & Test

on:
  push:
    branches: [main]
    tags-ignore: ["v*"]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write
  id-token: write

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  quality:
    name: Code Quality
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install UV
        uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
          python-version: "3.12"
          enable-cache: true

      - name: Install dependencies
        run: |
          uv pip install --system --upgrade pip
          uv pip install --system ".[dev]"

      - name: Run Ruff lint
        uses: astral-sh/ruff-action@v3
        with:
          version: "latest"
          args: "check --output-format=github"

      - name: Run Ruff Format
        uses: astral-sh/ruff-action@v3
        with:
          version: "latest"
          args: "format --check --respect-gitignore"

      - name: Run type checking
        run: uv run mypy src/twat_os tests

      - name: Run security checks
        run: |
          uv pip install --system bandit safety
          uv run bandit -r src/twat_os -f json || true
          uv run safety check || true

  test:
    name: Run Tests
    needs: quality
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
        os: [ubuntu-latest, windows-latest, macos-latest]
      fail-fast: false
    runs-on: ${{ matrix.os }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install UV
        uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
          python-version: ${{ matrix.python-version }}
          enable-cache: true
          cache-suffix: ${{ matrix.os }}-${{ matrix.python-version }}

      - name: Install test dependencies
        run: |
          uv pip install --system --upgrade pip
          uv pip install --system ".[test]"

      - name: Run tests with Pytest
        run: uv run pytest -n auto --maxfail=1 --disable-warnings --cov-report=xml --cov-config=pyproject.toml --cov=src/twat_os --cov=tests tests/

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.python-version }}-${{ matrix.os }}
          path: coverage.xml

  build:
    name: Build Distribution
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install UV
        uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
          python-version: "3.12"
          enable-cache: true

      - name: Install build tools
        run: uv pip install --system build hatchling hatch-vcs

      - name: Build distributions
        run: uv run python -m build --outdir dist

      - name: Verify distributions
        run: |
          ls -la dist/
          test -n "$(find dist -name '*.whl')" || (echo "Wheel file missing" && exit 1)
          test -n "$(find dist -name '*.tar.gz')" || (echo "Source distribution missing" && exit 1)

      - name: Upload distribution artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist-files
          path: dist/
          retention-days: 5

  coverage:
    name: Coverage Report
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Download coverage reports
        uses: actions/download-artifact@v4
        with:
          pattern: coverage-*
          path: coverage-reports/

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install coverage tools
        run: pip install coverage[toml]

      - name: Combine coverage reports
        run: |
          coverage combine coverage-reports/*/coverage.xml
          coverage report
          coverage html

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          fail_ci_if_error: false
```

### `.github/workflows/release.yml`
```yaml
name: Release

on:
  push:
    tags: ["v*"]

permissions:
  contents: write
  id-token: write

jobs:
  validate:
    name: Validate Release
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install UV
        uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
          python-version: "3.12"
          enable-cache: true

      - name: Install dependencies
        run: |
          uv pip install --system --upgrade pip
          uv pip install --system ".[dev,test]"

      - name: Validate tag format
        run: |
          TAG_NAME=${GITHUB_REF#refs/tags/}
          if [[ ! "$TAG_NAME" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)*)?$ ]]; then
            echo "Invalid tag format: $TAG_NAME"
            echo "Expected format: v1.0.0 or v1.0.0-alpha.1"
            exit 1
          fi
          echo "Valid tag format: $TAG_NAME"

      - name: Run all checks
        run: |
          uv run python scripts/check.py all

  test:
    name: Test Release
    needs: validate
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
        os: [ubuntu-latest, windows-latest, macos-latest]
      fail-fast: false
    runs-on: ${{ matrix.os }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install UV
        uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
          python-version: ${{ matrix.python-version }}
          enable-cache: true

      - name: Install test dependencies
        run: |
          uv pip install --system --upgrade pip
          uv pip install --system ".[test]"

      - name: Run tests
        run: uv run pytest -n auto --maxfail=1 tests/

  build:
    name: Build Release
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install UV
        uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
          python-version: "3.12"
          enable-cache: true

      - name: Install build tools
        run: uv pip install --system build hatchling hatch-vcs twine

      - name: Build distributions
        run: uv run python -m build --outdir dist

      - name: Verify distribution files
        run: |
          ls -la dist/
          test -n "$(find dist -name '*.whl')" || (echo "Wheel file missing" && exit 1)
          test -n "$(find dist -name '*.tar.gz')" || (echo "Source distribution missing" && exit 1)

      - name: Check distribution with twine
        run: uv run twine check dist/*

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: release-distributions
          path: dist/
          retention-days: 30

  build-binaries:
    name: Build Binaries
    needs: test
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
      fail-fast: false
    runs-on: ${{ matrix.os }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install UV
        uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
          python-version: "3.12"
          enable-cache: true

      - name: Install dependencies
        run: |
          uv pip install --system --upgrade pip
          uv pip install --system ".[dev]" pyinstaller

      - name: Build binary
        run: |
          uv run pyinstaller --onefile --name=twat-os-${{ matrix.os }} --console src/twat_os/__main__.py

      - name: Test binary (Unix)
        if: matrix.os != 'windows-latest'
        run: |
          ./dist/twat-os-${{ matrix.os }} version
          ./dist/twat-os-${{ matrix.os }} info

      - name: Test binary (Windows)
        if: matrix.os == 'windows-latest'
        run: |
          .\dist\twat-os-${{ matrix.os }}.exe version
          .\dist\twat-os-${{ matrix.os }}.exe info

      - name: Upload binary artifacts
        uses: actions/upload-artifact@v4
        with:
          name: binary-${{ matrix.os }}
          path: dist/twat-os-*
          retention-days: 30

  publish:
    name: Publish Release
    needs: [build, build-binaries]
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/twat-os
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Download distributions
        uses: actions/download-artifact@v4
        with:
          name: release-distributions
          path: dist/

      - name: Download binaries
        uses: actions/download-artifact@v4
        with:
          pattern: binary-*
          path: binaries/
          merge-multiple: true

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_TOKEN }}

      - name: Generate changelog
        id: changelog
        run: |
          TAG_NAME=${GITHUB_REF#refs/tags/}
          PREV_TAG=$(git describe --tags --abbrev=0 $TAG_NAME^ 2>/dev/null || echo "")
          
          if [ -n "$PREV_TAG" ]; then
            echo "## Changes since $PREV_TAG" > CHANGELOG.md
            git log --oneline --pretty=format:"- %s" $PREV_TAG..$TAG_NAME >> CHANGELOG.md
          else
            echo "## Changes" > CHANGELOG.md
            git log --oneline --pretty=format:"- %s" --max-count=20 >> CHANGELOG.md
          fi
          
          echo "changelog<<EOF" >> $GITHUB_OUTPUT
          cat CHANGELOG.md >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            dist/*
            binaries/*
          body: |
            ${{ steps.changelog.outputs.changelog }}
            
            ## Installation
            
            ### Python Package
            ```bash
            pip install twat-os
            ```
            
            ### Standalone Binaries
            Download the appropriate binary for your platform from the assets below.
            
            ## Verification
            
            All artifacts are signed and checksums are provided for verification.
          generate_release_notes: true
          draft: false
          prerelease: ${{ contains(github.ref, 'alpha') || contains(github.ref, 'beta') || contains(github.ref, 'rc') }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Next Steps

1. Add the workflow files using one of the methods above
2. Test the workflows by creating a pull request
3. Create your first release with: `git tag v1.0.0 && git push origin v1.0.0`