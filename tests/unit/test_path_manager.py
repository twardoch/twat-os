"""Unit tests for PathManager class."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from twat_os.paths import PathManager


class TestPathManager:
    """Test the PathManager class."""

    def test_init_without_package_name(self, mock_platformdirs: None) -> None:
        """Test PathManager initialization without package name."""
        manager = PathManager(create_dirs=False)
        assert manager.package_name is None
        assert not manager.create_dirs

    def test_init_with_package_name(self, mock_platformdirs: None) -> None:
        """Test PathManager initialization with package name."""
        manager = PathManager(package_name="test_package", create_dirs=False)
        assert manager.package_name == "test_package"

    def test_init_with_custom_config(self, sample_config_file: Path) -> None:
        """Test PathManager initialization with custom config file."""
        manager = PathManager(config_file=sample_config_file, create_dirs=False)
        assert manager.config["cache"]["base_dir"] == "/tmp/test_cache"

    def test_init_with_nonexistent_config_file(self) -> None:
        """Test PathManager initialization with nonexistent config file."""
        with pytest.raises(FileNotFoundError, match="Config file not found"):
            PathManager(config_file="/nonexistent/config.toml")

    def test_for_package_class_method(self, mock_platformdirs: None) -> None:
        """Test PathManager.for_package class method."""
        manager = PathManager.for_package("test_package")
        assert manager.package_name == "test_package"
        assert isinstance(manager, PathManager)

    def test_cache_configuration(self, mock_platformdirs: None) -> None:
        """Test cache configuration setup."""
        manager = PathManager(create_dirs=False)
        assert hasattr(manager, "cache")
        assert "cache/twat" in str(manager.cache.base_dir)

    def test_config_dir_configuration(self, mock_platformdirs: None) -> None:
        """Test config directory configuration setup."""
        manager = PathManager(create_dirs=False)
        assert hasattr(manager, "config_dir")
        assert "config/twat" in str(manager.config_dir.base_dir)

    def test_data_configuration(self, mock_platformdirs: None) -> None:
        """Test data configuration setup."""
        manager = PathManager(create_dirs=False)
        assert hasattr(manager, "data")
        assert "data/twat" in str(manager.data.base_dir)

    def test_temp_configuration(self, mock_platformdirs: None) -> None:
        """Test temp configuration setup."""
        manager = PathManager(create_dirs=False)
        assert hasattr(manager, "temp")
        assert "runtime/twat" in str(manager.temp.base_dir)

    def test_genai_configuration(self, mock_platformdirs: None) -> None:
        """Test GenAI configuration setup."""
        manager = PathManager(create_dirs=False)
        assert hasattr(manager, "genai")
        assert "genai/loras" in str(manager.genai.lora_dir)
        assert "genai/models" in str(manager.genai.model_dir)

    def test_logs_configuration(self, mock_platformdirs: None) -> None:
        """Test logs configuration setup."""
        manager = PathManager(create_dirs=False)
        assert hasattr(manager, "logs")
        assert "state/twat/logs" in str(manager.logs.base_dir)

    def test_package_specific_paths(self, mock_platformdirs: None) -> None:
        """Test package-specific path generation."""
        manager = PathManager(package_name="test_package", create_dirs=False)
        assert manager.cache.package_dir is not None
        assert "test_package" in str(manager.cache.package_dir)
        assert manager.config_dir.package_dir is not None
        assert "test_package" in str(manager.config_dir.package_dir)

    def test_package_paths_without_package_name(self, mock_platformdirs: None) -> None:
        """Test package-specific paths without package name."""
        manager = PathManager(create_dirs=False)
        assert manager.cache.package_dir is None
        assert manager.config_dir.package_dir is None

    def test_get_path_method(self, mock_platformdirs: None) -> None:
        """Test get_path method."""
        manager = PathManager(create_dirs=False)
        cache_path = manager.get_path("cache", "base_dir")
        assert isinstance(cache_path, Path)
        assert "cache/twat" in str(cache_path)

    def test_get_path_with_package_dir(self, mock_platformdirs: None) -> None:
        """Test get_path method with package directory."""
        manager = PathManager(package_name="test_package", create_dirs=False)
        package_path = manager.get_path("cache", "package_dir")
        assert isinstance(package_path, Path)
        assert "test_package" in str(package_path)

    def test_get_path_with_none_package_dir(self, mock_platformdirs: None) -> None:
        """Test get_path method with None package directory."""
        manager = PathManager(create_dirs=False)
        with pytest.raises(ValueError, match="Path for 'cache.package_dir' is None"):
            manager.get_path("cache", "package_dir")

    def test_get_path_with_invalid_category(self, mock_platformdirs: None) -> None:
        """Test get_path method with invalid category."""
        manager = PathManager(create_dirs=False)
        with pytest.raises(AttributeError):
            manager.get_path("invalid_category", "base_dir")

    def test_get_path_with_invalid_key(self, mock_platformdirs: None) -> None:
        """Test get_path method with invalid key."""
        manager = PathManager(create_dirs=False)
        with pytest.raises(AttributeError):
            manager.get_path("cache", "invalid_key")

    def test_get_path_with_genai_paths(self, mock_platformdirs: None) -> None:
        """Test get_path method with GenAI paths."""
        manager = PathManager(create_dirs=False)
        lora_path = manager.get_path("genai", "lora_dir")
        model_path = manager.get_path("genai", "model_dir")
        output_path = manager.get_path("genai", "output_dir")
        
        assert isinstance(lora_path, Path)
        assert isinstance(model_path, Path)
        assert isinstance(output_path, Path)
        assert "genai/loras" in str(lora_path)
        assert "genai/models" in str(model_path)

    def test_repr_without_package_name(self, mock_platformdirs: None) -> None:
        """Test __repr__ method without package name."""
        manager = PathManager(create_dirs=False)
        repr_str = repr(manager)
        assert repr_str == "PathManager"

    def test_repr_with_package_name(self, mock_platformdirs: None) -> None:
        """Test __repr__ method with package name."""
        manager = PathManager(package_name="test_package", create_dirs=False)
        repr_str = repr(manager)
        assert repr_str == "PathManager for package 'test_package'"

    def test_environment_variable_expansion(self, temp_dir: Path) -> None:
        """Test environment variable expansion in paths."""
        test_var = str(temp_dir / "test_env")
        with patch.dict(os.environ, {"TEST_HOME": test_var}):
            config_content = """
[cache]
base_dir = "${TEST_HOME}/cache"
package_dir = "${TEST_HOME}/cache/{package_name}"
"""
            config_file = temp_dir / "env_config.toml"
            config_file.write_text(config_content)
            
            manager = PathManager(
                package_name="test_package",
                config_file=config_file,
                create_dirs=False
            )
            
            assert str(manager.cache.base_dir).startswith(test_var)
            assert str(manager.cache.package_dir).startswith(test_var)
            assert "test_package" in str(manager.cache.package_dir)

    def test_user_home_expansion(self, temp_dir: Path) -> None:
        """Test user home directory expansion in paths."""
        config_content = """
[cache]
base_dir = "~/test_cache"
package_dir = "~/test_cache/{package_name}"
"""
        config_file = temp_dir / "home_config.toml"
        config_file.write_text(config_content)
        
        manager = PathManager(
            package_name="test_package",
            config_file=config_file,
            create_dirs=False
        )
        
        # The paths should be expanded (not contain literal ~)
        assert "~" not in str(manager.cache.base_dir)
        assert "~" not in str(manager.cache.package_dir)
        assert "test_package" in str(manager.cache.package_dir)

    def test_directory_creation_enabled(self, temp_dir: Path) -> None:
        """Test directory creation when enabled."""
        config_content = f"""
[cache]
base_dir = "{temp_dir}/test_cache"
package_dir = "{temp_dir}/test_cache/{{package_name}}"
"""
        config_file = temp_dir / "creation_config.toml"
        config_file.write_text(config_content)
        
        manager = PathManager(
            package_name="test_package",
            config_file=config_file,
            create_dirs=True
        )
        
        assert manager.cache.base_dir.exists()
        assert manager.cache.package_dir.exists()

    def test_directory_creation_disabled(self, temp_dir: Path) -> None:
        """Test directory creation when disabled."""
        config_content = f"""
[cache]
base_dir = "{temp_dir}/test_cache_no_create"
package_dir = "{temp_dir}/test_cache_no_create/{{package_name}}"
"""
        config_file = temp_dir / "no_creation_config.toml"
        config_file.write_text(config_content)
        
        manager = PathManager(
            package_name="test_package",
            config_file=config_file,
            create_dirs=False
        )
        
        assert not manager.cache.base_dir.exists()
        assert not manager.cache.package_dir.exists()