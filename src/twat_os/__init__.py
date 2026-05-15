"""twat-os: OS-aware path management for the twat ecosystem."""

from __future__ import annotations
from .__version__ import __version__


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


def main() -> None:
    """CLI entry point for twat-os."""
    from twat_os.__main__ import main as cli_main

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
