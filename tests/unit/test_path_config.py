"""Unit tests for PathConfig classes."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from twat_os.paths import (
    CacheConfig,
    ConfigDirConfig,
    DataDirConfig,
    GenAIConfig,
    LogConfig,
    PathConfig,
    TempDirConfig,
)


class TestPathConfig:
    """Test the base PathConfig class."""

    def test_expand_path_with_user_home(self, temp_dir: Path) -> None:
        """Test path expansion with user home directory."""
        with patch("pathlib.Path.expanduser") as mock_expanduser:
            mock_expanduser.return_value = temp_dir / "user"
            result = PathConfig.expand_path("~/test/path")
            assert result == temp_dir / "user/test/path"

    def test_expand_path_with_env_vars(self, temp_dir: Path) -> None:
        """Test path expansion with environment variables."""
        with patch.dict(os.environ, {"TEST_VAR": str(temp_dir)}):
            result = PathConfig.expand_path("${TEST_VAR}/test/path")
            assert result == temp_dir / "test/path"

    def test_expand_path_with_none(self) -> None:
        """Test path expansion with None input."""
        result = PathConfig.expand_path(None)
        assert result is None

    def test_expand_path_with_path_object(self, temp_dir: Path) -> None:
        """Test path expansion with Path object input."""
        test_path = temp_dir / "test"
        result = PathConfig.expand_path(test_path)
        assert result == test_path

    def test_directory_creation_enabled(self, temp_dir: Path) -> None:
        """Test directory creation when enabled."""
        base_dir = temp_dir / "base"
        package_dir = temp_dir / "package"
        
        config = PathConfig(
            base_dir=base_dir,
            package_dir=package_dir,
            create_if_missing=True
        )
        
        assert base_dir.exists()
        assert package_dir.exists()

    def test_directory_creation_disabled(self, temp_dir: Path) -> None:
        """Test directory creation when disabled."""
        base_dir = temp_dir / "base"
        package_dir = temp_dir / "package"
        
        config = PathConfig(
            base_dir=base_dir,
            package_dir=package_dir,
            create_if_missing=False
        )
        
        assert not base_dir.exists()
        assert not package_dir.exists()

    def test_directory_creation_with_none_package_dir(self, temp_dir: Path) -> None:
        """Test directory creation with None package_dir."""
        base_dir = temp_dir / "base"
        
        config = PathConfig(
            base_dir=base_dir,
            package_dir=None,
            create_if_missing=True
        )
        
        assert base_dir.exists()


class TestCacheConfig:
    """Test the CacheConfig class."""

    def test_default_cache_dir(self, mock_platformdirs: None) -> None:
        """Test default cache directory creation."""
        config = CacheConfig(create_if_missing=False)
        assert "cache/twat" in str(config.base_dir)

    def test_custom_cache_dir(self, temp_dir: Path) -> None:
        """Test custom cache directory."""
        custom_dir = temp_dir / "custom_cache"
        config = CacheConfig(base_dir=custom_dir, create_if_missing=False)
        assert config.base_dir == custom_dir


class TestConfigDirConfig:
    """Test the ConfigDirConfig class."""

    def test_default_config_dir(self, mock_platformdirs: None) -> None:
        """Test default config directory creation."""
        config = ConfigDirConfig(create_if_missing=False)
        assert "config/twat" in str(config.base_dir)

    def test_custom_config_dir(self, temp_dir: Path) -> None:
        """Test custom config directory."""
        custom_dir = temp_dir / "custom_config"
        config = ConfigDirConfig(base_dir=custom_dir, create_if_missing=False)
        assert config.base_dir == custom_dir


class TestDataDirConfig:
    """Test the DataDirConfig class."""

    def test_default_data_dir(self, mock_platformdirs: None) -> None:
        """Test default data directory creation."""
        config = DataDirConfig(create_if_missing=False)
        assert "data/twat" in str(config.base_dir)

    def test_custom_data_dir(self, temp_dir: Path) -> None:
        """Test custom data directory."""
        custom_dir = temp_dir / "custom_data"
        config = DataDirConfig(base_dir=custom_dir, create_if_missing=False)
        assert config.base_dir == custom_dir


class TestTempDirConfig:
    """Test the TempDirConfig class."""

    def test_default_temp_dir(self, mock_platformdirs: None) -> None:
        """Test default temp directory creation."""
        config = TempDirConfig(create_if_missing=False)
        assert "runtime/twat" in str(config.base_dir)

    def test_custom_temp_dir(self, temp_dir: Path) -> None:
        """Test custom temp directory."""
        custom_dir = temp_dir / "custom_temp"
        config = TempDirConfig(base_dir=custom_dir, create_if_missing=False)
        assert config.base_dir == custom_dir


class TestGenAIConfig:
    """Test the GenAIConfig class."""

    def test_default_genai_dirs(self, mock_platformdirs: None) -> None:
        """Test default GenAI directory creation."""
        config = GenAIConfig(create_if_missing=False)
        assert "data/twat" in str(config.base_dir)
        assert "genai/loras" in str(config.lora_dir)
        assert "genai/models" in str(config.model_dir)
        assert "Pictures/twat_genai" in str(config.output_dir)

    def test_custom_genai_dirs(self, temp_dir: Path) -> None:
        """Test custom GenAI directories."""
        base_dir = temp_dir / "base"
        lora_dir = temp_dir / "loras"
        model_dir = temp_dir / "models"
        output_dir = temp_dir / "output"
        
        config = GenAIConfig(
            base_dir=base_dir,
            lora_dir=lora_dir,
            model_dir=model_dir,
            output_dir=output_dir,
            create_if_missing=False
        )
        
        assert config.base_dir == base_dir
        assert config.lora_dir == lora_dir
        assert config.model_dir == model_dir
        assert config.output_dir == output_dir

    def test_genai_directory_creation(self, temp_dir: Path) -> None:
        """Test GenAI directory creation."""
        base_dir = temp_dir / "base"
        lora_dir = temp_dir / "loras"
        model_dir = temp_dir / "models"
        output_dir = temp_dir / "output"
        
        config = GenAIConfig(
            base_dir=base_dir,
            lora_dir=lora_dir,
            model_dir=model_dir,
            output_dir=output_dir,
            create_if_missing=True
        )
        
        assert base_dir.exists()
        assert lora_dir.exists()
        assert model_dir.exists()
        assert output_dir.exists()


class TestLogConfig:
    """Test the LogConfig class."""

    def test_default_log_dir(self, mock_platformdirs: None) -> None:
        """Test default log directory creation."""
        config = LogConfig(create_if_missing=False)
        assert "state/twat/logs" in str(config.base_dir)

    def test_custom_log_dir(self, temp_dir: Path) -> None:
        """Test custom log directory."""
        custom_dir = temp_dir / "custom_logs"
        config = LogConfig(base_dir=custom_dir, create_if_missing=False)
        assert config.base_dir == custom_dir