#!/usr/bin/env -S uv run
# /// script
# dependencies = ["pydantic", "platformdirs"]
# ///
"""Platform-aware path management for twat packages.

Every OS stores application data in different places.  On macOS user caches
live under ``~/Library/Caches``; on Linux under ``~/.cache``; on Windows under
``%LOCALAPPDATA%``.  Hard-coding these paths breaks cross-platform portability.

This module uses `platformdirs <https://platformdirs.readthedocs.io>`_ (the
successor to ``appdirs``) to resolve the correct OS-specific directories at
runtime, then exposes them through typed Pydantic models.

Directory categories
---------------------
cache
    Temporary data that can be regenerated.  Cleared by the OS under storage
    pressure.  ``~/.cache/twat`` on Linux.
config
    User configuration files.  ``~/.config/twat`` on Linux.
data
    Persistent application data (databases, downloaded assets).
    ``~/.local/share/twat`` on Linux.
temp
    Short-lived runtime files (sockets, PID files).
logs
    Log files.
genai
    Specialised paths for AI model weights, LoRA files, and generated images.

Usage::

    from twat_os.paths import PathManager

    pm = PathManager.for_package("my_plugin")
    pm.cache.package_dir.mkdir(parents=True, exist_ok=True)
    model_file = pm.data.package_dir / "model.bin"

Directories are created automatically when ``create_dirs=True`` (the default).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import platformdirs
import tomli
from pydantic import BaseModel, Field, field_validator, model_validator

if TYPE_CHECKING:
    from typing_extensions import Self

# Load default paths from TOML
PATHS_TOML = Path(__file__).parent / "paths.toml"
DEFAULT_PATHS = tomli.loads(PATHS_TOML.read_text())


class PathConfig(BaseModel):
    """Base configuration for path settings."""

    base_dir: Path
    package_dir: Path | None = None
    create_if_missing: bool = True

    @field_validator("base_dir", "package_dir", mode="before")
    @classmethod
    def expand_path(cls, v: str | Path | None) -> Path | None:
        """Expand user home and environment variables in paths.

        Runs before Pydantic coerces the value to ``Path`` so that string
        values coming from TOML (e.g. ``"~/.cache/twat"``) are fully expanded
        before being stored.  The ``~`` component is replaced character-by-
        character so that a mocked :py:meth:`pathlib.Path.expanduser` only
        substitutes the home prefix while preserving the rest of the path.
        """
        if v is None:
            return None
        s = str(v)
        # Expand ~ by replacing only the leading ~ token, keeping the suffix.
        # This ensures test mocks of Path.expanduser() work correctly.
        if s.startswith("~"):
            home = str(Path("~").expanduser())
            s = home + s[1:]
        # Expand $VAR / ${VAR} environment variables.
        s = os.path.expandvars(s)
        return Path(s)

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

    base_dir: Path = Field(default_factory=lambda: Path(platformdirs.user_cache_dir()) / "twat")


class ConfigDirConfig(PathConfig):
    """Configuration for config directories."""

    base_dir: Path = Field(default_factory=lambda: Path(platformdirs.user_config_dir()) / "twat")


class DataDirConfig(PathConfig):
    """Configuration for data directories."""

    base_dir: Path = Field(default_factory=lambda: Path(platformdirs.user_data_dir()) / "twat")


class TempDirConfig(PathConfig):
    """Configuration for temporary directories."""

    base_dir: Path = Field(default_factory=lambda: Path(platformdirs.user_runtime_dir()) / "twat")


class GenAIConfig(PathConfig):
    """Configuration for GenAI-specific paths."""

    base_dir: Path = Field(default_factory=lambda: Path(platformdirs.user_data_dir()) / "twat/genai")
    lora_dir: Path = Field(default_factory=lambda: Path(platformdirs.user_data_dir()) / "twat/genai/loras")
    model_dir: Path = Field(default_factory=lambda: Path(platformdirs.user_data_dir()) / "twat/genai/models")
    output_dir: Path = Field(default_factory=lambda: Path.home() / "Pictures/twat_genai")

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

    base_dir: Path = Field(default_factory=lambda: Path(platformdirs.user_state_dir()) / "twat/logs")


class PathManager:
    """Central manager for all path configurations."""

    def __init__(
        self,
        package_name: str | None = None,
        config_file: str | Path | None = None,
        *,
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

        # Load user-supplied config (may be partial — only some sections).
        if config_file:
            config_path = Path(config_file)
            if not config_path.exists():
                msg = f"Config file not found: {config_file}"
                raise FileNotFoundError(msg)
            self._user_config: dict | None = tomli.loads(config_path.read_text())
        else:
            self._user_config = None

        # Provide a merged view (section-level) for backward-compat attribute
        # access (e.g. ``manager.config["cache"]["base_dir"]``).
        self.config: dict = {**DEFAULT_PATHS, **(self._user_config or {})}

        # Initialize path configurations
        self._init_paths()

    def _init_paths(self) -> None:
        """Initialize all path configurations.

        When no config file was supplied (``_user_config is None``), each
        ``PathConfig`` subclass is constructed *without* an explicit
        ``base_dir`` so that its ``Field(default_factory=…)`` kicks in and
        calls ``platformdirs`` at runtime.  This lets ``mock_platformdirs``
        fixtures in tests produce the expected values.

        When a (possibly partial) config file was supplied, missing sections
        fall back to ``DEFAULT_PATHS`` — so the ``KeyError`` that arose from
        accessing ``self.config["config"]`` on a single-section file is gone.
        """

        def format_path(path_str: str) -> Path | None:
            """Expand ``~`` / env-vars in *path_str* then fill ``{package_name}``."""
            if not self.package_name:
                return None
            s = path_str
            if s.startswith("~"):
                s = str(Path("~").expanduser()) + s[1:]
            s = os.path.expandvars(s)
            return Path(s.format(package_name=self.package_name))

        def eff_section(key: str) -> dict | None:
            """Return the effective config section for *key*.

            * No user config → ``None`` (let field ``default_factory`` decide).
            * User config provided but section absent → fall back to
              ``DEFAULT_PATHS[key]`` so partial configs never raise
              ``KeyError``.
            """
            if self._user_config is None:
                return None
            return self._user_config.get(key, DEFAULT_PATHS.get(key, {}))

        def std_kwargs(section_key: str) -> dict:
            """Build constructor kwargs for a standard PathConfig subclass."""
            kw: dict = {"create_if_missing": self.create_dirs}
            sec = eff_section(section_key)
            # Only pass base_dir when we have an explicit config; otherwise
            # the field default_factory uses platformdirs at call time.
            if sec is not None and "base_dir" in sec:
                kw["base_dir"] = sec["base_dir"]
            # package_dir: derive from user config section if present, else
            # from DEFAULT_PATHS template (always contains {package_name}).
            if self._user_config is not None:
                tmpl_sec = self._user_config.get(section_key, DEFAULT_PATHS.get(section_key, {}))
            else:
                tmpl_sec = DEFAULT_PATHS.get(section_key, {})
            tmpl = tmpl_sec.get("package_dir")
            if tmpl is not None:
                kw["package_dir"] = format_path(tmpl)
            return kw

        self.cache = CacheConfig(**std_kwargs("cache"))
        self.config_dir = ConfigDirConfig(**std_kwargs("config"))
        self.data = DataDirConfig(**std_kwargs("data"))
        self.temp = TempDirConfig(**std_kwargs("temp"))
        self.logs = LogConfig(**std_kwargs("logs"))

        # GenAI: uses the data section's base_dir when a config file is given;
        # otherwise all fields use their own default_factory (platformdirs).
        genai_kw: dict = {"create_if_missing": self.create_dirs}
        if self._user_config is not None:
            data_sec = self._user_config.get("data", DEFAULT_PATHS.get("data", {}))
            if data_sec.get("base_dir"):
                genai_kw["base_dir"] = data_sec["base_dir"]
            genai_sec = self._user_config.get("genai", DEFAULT_PATHS.get("genai", {}))
            for key in ("lora_dir", "model_dir", "output_dir"):
                val = genai_sec.get(key)
                if val:
                    genai_kw[key] = val
        self.genai = GenAIConfig(**genai_kw)

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
        path_value = getattr(config, key)
        if not isinstance(path_value, Path):
            # This case should ideally not happen if Pydantic models are correct
            # and keys always point to Path objects or None (for package_dir sometimes).
            # However, to satisfy type checker for dynamic getattr:
            if path_value is None and key == "package_dir":  # package_dir can be None
                # This function is typed to return Path, so None is not allowed here.
                # This indicates a potential design issue or misuse of get_path for optional paths.
                # For now, raising an error is safer than returning None.
                msg = f"Path for '{category}.{key}' is None, but Path type was expected."
                raise ValueError(msg)
            msg = f"Unexpected type for '{category}.{key}': {type(path_value)}. Expected Path."
            raise TypeError(msg)
        return path_value  # Cast is redundant due to isinstance check

    @classmethod
    def for_package(
        cls,
        package_name: str,
        config_file: str | Path | None = None,
        *,
        create_dirs: bool = True,
    ) -> PathManager:
        """Create a PathManager instance for a specific package.

        Args:
            package_name: Package name
            config_file: Optional path to custom config file
            create_dirs: Whether to create directories if they don't exist

        Returns:
            PathManager instance configured for the package
        """
        return cls(package_name=package_name, config_file=config_file, create_dirs=create_dirs)

    def __repr__(self) -> str:
        """Return string representation of PathManager."""
        package_info = f" for package '{self.package_name}'" if self.package_name else ""
        return f"PathManager{package_info}"
