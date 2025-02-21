#!/usr/bin/env -S uv run
# /// script
# dependencies = ["pydantic", "platformdirs"]
# ///
"""Path management for twat packages.

This module provides a centralized way to manage paths for various twat packages.
It handles path resolution, validation, and creation of directories as needed.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Self

import platformdirs
import tomli
from pydantic import BaseModel, Field, field_validator, model_validator

# Load default paths from TOML
PATHS_TOML = Path(__file__).parent / "paths.toml"
DEFAULT_PATHS = tomli.loads(PATHS_TOML.read_text())


class PathConfig(BaseModel):
    """Base configuration for path settings."""

    base_dir: Path
    package_dir: Path | None = None
    create_if_missing: bool = True

    @field_validator("base_dir", "package_dir")
    @classmethod
    def expand_path(cls, v: str | Path | None) -> Path | None:
        """Expand user and environment variables in paths."""
        if v is None:
            return None
        if isinstance(v, str):
            # Expand both ~ and environment variables
            expanded = os.path.expandvars(os.path.expanduser(v))
            return Path(expanded)
        return v

    @model_validator(mode="after")
    def validate_and_create_dirs(self) -> Self:
        """Create directories if they don't exist and creation is enabled."""
        if self.create_if_missing:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            if self.package_dir:
                self.package_dir.mkdir(parents=True, exist_ok=True)
        return self


class CacheConfig(PathConfig):
    """Configuration for cache directories."""

    base_dir: Path = Field(
        default_factory=lambda: Path(platformdirs.user_cache_dir()) / "twat"
    )


class ConfigDirConfig(PathConfig):
    """Configuration for config directories."""

    base_dir: Path = Field(
        default_factory=lambda: Path(platformdirs.user_config_dir()) / "twat"
    )


class DataDirConfig(PathConfig):
    """Configuration for data directories."""

    base_dir: Path = Field(
        default_factory=lambda: Path(platformdirs.user_data_dir()) / "twat"
    )


class TempDirConfig(PathConfig):
    """Configuration for temporary directories."""

    base_dir: Path = Field(
        default_factory=lambda: Path(platformdirs.user_runtime_dir()) / "twat"
    )


class GenAIConfig(PathConfig):
    """Configuration for GenAI-specific paths."""

    lora_dir: Path = Field(
        default_factory=lambda: Path(platformdirs.user_data_dir()) / "twat/genai/loras"
    )
    model_dir: Path = Field(
        default_factory=lambda: Path(platformdirs.user_data_dir()) / "twat/genai/models"
    )
    output_dir: Path = Field(
        default_factory=lambda: Path.home() / "Pictures/twat_genai"
    )

    @model_validator(mode="after")
    def validate_and_create_all_dirs(self) -> Self:
        """Create all GenAI directories if enabled."""
        if self.create_if_missing:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.lora_dir.mkdir(parents=True, exist_ok=True)
            self.model_dir.mkdir(parents=True, exist_ok=True)
            self.output_dir.mkdir(parents=True, exist_ok=True)
        return self


class LogConfig(PathConfig):
    """Configuration for log directories."""

    base_dir: Path = Field(
        default_factory=lambda: Path(platformdirs.user_state_dir()) / "twat/logs"
    )


class PathManager:
    """Central manager for all path configurations."""

    def __init__(
        self,
        package_name: str | None = None,
        config_file: str | Path | None = None,
        create_dirs: bool = True,
    ) -> None:
        """Initialize path manager.

        Args:
            package_name: Optional package name for package-specific paths
            config_file: Optional path to custom config file
            create_dirs: Whether to create directories if they don't exist
        """
        self.package_name = package_name
        self.create_dirs = create_dirs

        # Load config
        if config_file:
            config_path = Path(config_file)
            if not config_path.exists():
                msg = f"Config file not found: {config_file}"
                raise FileNotFoundError(msg)
            self.config = tomli.loads(config_path.read_text())
        else:
            self.config = DEFAULT_PATHS

        # Initialize path configurations
        self._init_paths()

    def _init_paths(self) -> None:
        """Initialize all path configurations."""

        # Helper to format package-specific paths
        def format_path(path_str: str) -> Path | None:
            if not self.package_name:
                return None
            expanded = os.path.expandvars(os.path.expanduser(path_str))
            return Path(expanded.format(package_name=self.package_name))

        # Initialize configurations
        self.cache = CacheConfig(
            base_dir=self.config["cache"]["base_dir"],
            package_dir=format_path(self.config["cache"]["package_dir"]),
            create_if_missing=self.create_dirs,
        )

        self.config_dir = ConfigDirConfig(
            base_dir=self.config["config"]["base_dir"],
            package_dir=format_path(self.config["config"]["package_dir"]),
            create_if_missing=self.create_dirs,
        )

        self.data = DataDirConfig(
            base_dir=self.config["data"]["base_dir"],
            package_dir=format_path(self.config["data"]["package_dir"]),
            create_if_missing=self.create_dirs,
        )

        self.temp = TempDirConfig(
            base_dir=self.config["temp"]["base_dir"],
            package_dir=format_path(self.config["temp"]["package_dir"]),
            create_if_missing=self.create_dirs,
        )

        self.genai = GenAIConfig(
            base_dir=self.config["data"]["base_dir"],
            lora_dir=self.config["genai"]["lora_dir"],
            model_dir=self.config["genai"]["model_dir"],
            output_dir=self.config["genai"]["output_dir"],
            create_if_missing=self.create_dirs,
        )

        self.logs = LogConfig(
            base_dir=self.config["logs"]["base_dir"],
            package_dir=format_path(self.config["logs"]["package_dir"]),
            create_if_missing=self.create_dirs,
        )

    def get_path(self, category: str, key: str = "base_dir") -> Path:
        """Get a specific path by category and key.

        Args:
            category: Path category (cache, config, data, temp, genai, logs)
            key: Path key within the category (base_dir, package_dir, etc.)

        Returns:
            Resolved path

        Raises:
            AttributeError: If category or key doesn't exist
        """
        config = getattr(self, category)
        return getattr(config, key)

    @classmethod
    def for_package(
        cls, package_name: str, config_file: str | Path | None = None
    ) -> PathManager:
        """Create a PathManager instance for a specific package.

        Args:
            package_name: Package name
            config_file: Optional path to custom config file

        Returns:
            PathManager instance configured for the package
        """
        return cls(package_name=package_name, config_file=config_file)

    def __repr__(self) -> str:
        """Return string representation of PathManager."""
        package_info = (
            f" for package '{self.package_name}'" if self.package_name else ""
        )
        return f"PathManager{package_info}"
