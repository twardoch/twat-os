# PLAN.md - Git-Tag-Based Semversioning Implementation

## Project Overview
Transform the twat-os Python package to implement comprehensive git-tag-based semversioning with robust testing, build automation, and multiplatform release capabilities.

## Current State Analysis
- **Package**: Python library for OS-aware path management
- **Build System**: Hatch with VCS versioning (already configured)
- **Existing CI/CD**: Basic GitHub Actions for testing and PyPI releases
- **Testing**: Minimal test suite (only version check)
- **Release**: Basic git tag-based PyPI releases

## Technical Architecture Decisions

### 1. Semversioning Strategy
- **Git Tags**: Use `v{major}.{minor}.{patch}` format (e.g., `v1.0.0`)
- **Version Source**: Hatch VCS plugin (already configured)
- **Pre-release**: Support alpha/beta/rc tags (e.g., `v1.0.0-alpha.1`)
- **Version File**: Auto-generated `__version__.py` by Hatch

### 2. Testing Framework
- **Framework**: pytest (already configured)
- **Coverage**: pytest-cov with XML reports
- **Test Types**: Unit, integration, and property-based tests
- **Environments**: Python 3.10, 3.11, 3.12 across multiple OS

### 3. Build and Release Pipeline
- **Local Scripts**: Convenient scripts for build, test, and release
- **CI/CD**: Enhanced GitHub Actions with matrix testing
- **Artifacts**: Source distributions and wheels
- **Multiplatform**: Support for Linux, macOS, and Windows

## Implementation Phases

### Phase 1: Enhanced Testing Infrastructure
- **Comprehensive Test Suite**
  - Unit tests for `PathManager` class
  - Integration tests for path resolution
  - Configuration tests for TOML parsing
  - Cross-platform compatibility tests
  - Property-based testing for path validation
  - Mock tests for OS-specific behavior

- **Test Organization**
  - `tests/unit/` - Unit tests for individual components
  - `tests/integration/` - Integration tests
  - `tests/conftest.py` - Shared fixtures and configuration
  - `tests/test_paths.py` - Core path management tests
  - `tests/test_config.py` - Configuration handling tests
  - `tests/test_platform.py` - Platform-specific tests

### Phase 2: Build and Release Scripts
- **Local Development Scripts**
  - `scripts/build.py` - Build distributions locally
  - `scripts/test.py` - Run comprehensive test suite
  - `scripts/release.py` - Cut releases with version validation
  - `scripts/check.py` - Pre-commit checks (lint, type, test)

- **Version Management**
  - Validate git tag format before release
  - Ensure clean working directory
  - Generate changelog from git history
  - Update version-dependent files

### Phase 3: Enhanced CI/CD Pipeline
- **Multi-OS Testing Matrix**
  - Test across Ubuntu, macOS, and Windows
  - Multiple Python versions (3.10, 3.11, 3.12)
  - Cross-platform path behavior validation

- **Release Automation**
  - Automated PyPI publishing on git tags
  - GitHub Releases with artifacts
  - Changelog generation
  - Security scanning and dependency checks

### Phase 4: Multiplatform Binary Support
- **CLI Tool Enhancement**
  - Implement missing `__main__.py` functionality
  - Create standalone executable with PyInstaller
  - Cross-platform binary compilation

- **Distribution Artifacts**
  - Python wheels for all platforms
  - Source distributions
  - Standalone executables for major platforms
  - Installation scripts for easy deployment

## Specific Implementation Details

### Test Coverage Requirements
- **Minimum Coverage**: 90% code coverage
- **Critical Components**: 100% coverage for core path logic
- **Edge Cases**: Comprehensive testing of OS-specific behaviors
- **Performance**: Benchmark tests for path resolution speed

### Version Validation Rules
- **Tag Format**: Must match `v\d+\.\d+\.\d+(-\w+\.\d+)?`
- **Increment Logic**: Validate semantic versioning increments
- **Branch Protection**: Only allow releases from main branch
- **Clean State**: Require clean working directory

### Release Artifact Requirements
- **Python Packages**: Source distribution and universal wheel
- **Binary Executables**: Platform-specific standalone binaries
- **Documentation**: Auto-generated API docs and changelog
- **Security**: Signed releases with checksums

### Cross-Platform Compatibility
- **Path Handling**: Validate behavior on Windows, macOS, Linux
- **Directory Creation**: Test permission handling across OS
- **Configuration**: Ensure TOML parsing works uniformly
- **Dependencies**: Verify all dependencies are cross-platform

## Success Criteria
1. **Comprehensive Testing**: 90%+ code coverage with multi-OS testing
2. **Automated Releases**: One-command local releases and automated CI/CD
3. **Multiplatform Support**: Working binaries for Linux, macOS, Windows
4. **Developer Experience**: Simple scripts for build, test, and release
5. **Version Management**: Robust git-tag-based semversioning
6. **Quality Assurance**: Automated linting, type checking, and security scanning

## Future Considerations
- **Performance Optimization**: Profile and optimize path resolution
- **Documentation**: Comprehensive API documentation with examples
- **Plugin System**: Enhanced integration with twat framework
- **Configuration Management**: Advanced TOML configuration features
- **Monitoring**: Release metrics and usage analytics