"""twat-os: OS-aware path management for the twat ecosystem."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from twat_os.paths import (
    CacheConfig,
    ConfigDirConfig,
    DataDirConfig,
    GenAIConfig,
    LogConfig,
    PathConfig,
    PathManager,
    TempDirConfig,
)

try:
    __version__ = version("twat-os")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"


def main() -> None:
    """CLI entry point for twat-os."""
    from twat_os.__main__ import main as cli_main  # noqa: PLC0415

    cli_main()


__all__ = [
    "CacheConfig",
    "ConfigDirConfig",
    "DataDirConfig",
    "GenAIConfig",
    "LogConfig",
    "PathConfig",
    "PathManager",
    "TempDirConfig",
    "__version__",
    "main",
]
