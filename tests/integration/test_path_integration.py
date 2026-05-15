"""Integration tests for path management functionality."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from twat_os.paths import PathManager


class TestPathIntegration:
    """Integration tests for PathManager functionality."""

    def test_end_to_end_path_creation(self, temp_dir: Path) -> None:
        """Test end-to-end path creation and usage."""
        # Create a custom config
        config_content = f"""
[cache]
base_dir = "{temp_dir}/app_cache"
package_dir = "{temp_dir}/app_cache/{{package_name}}"

[config]
base_dir = "{temp_dir}/app_config"
package_dir = "{temp_dir}/app_config/{{package_name}}"

[data]
base_dir = "{temp_dir}/app_data"
package_dir = "{temp_dir}/app_data/{{package_name}}"

[temp]
base_dir = "{temp_dir}/app_temp"
package_dir = "{temp_dir}/app_temp/{{package_name}}"

[genai]
lora_dir = "{temp_dir}/app_genai/loras"
model_dir = "{temp_dir}/app_genai/models"
output_dir = "{temp_dir}/app_genai/output"

[logs]
base_dir = "{temp_dir}/app_logs"
package_dir = "{temp_dir}/app_logs/{{package_name}}"
"""
        config_file = temp_dir / "app_config.toml"
        config_file.write_text(config_content)

        # Create PathManager for a specific package
        manager = PathManager.for_package("my_app", config_file=config_file)

        # Verify all directories were created
        assert manager.cache.base_dir.exists()
        assert manager.cache.package_dir.exists()
        assert manager.config_dir.base_dir.exists()
        assert manager.config_dir.package_dir.exists()
        assert manager.data.base_dir.exists()
        assert manager.data.package_dir.exists()
        assert manager.temp.base_dir.exists()
        assert manager.temp.package_dir.exists()
        assert manager.genai.lora_dir.exists()
        assert manager.genai.model_dir.exists()
        assert manager.genai.output_dir.exists()
        assert manager.logs.base_dir.exists()
        assert manager.logs.package_dir.exists()

        # Verify package-specific paths contain the package name
        assert "my_app" in str(manager.cache.package_dir)
        assert "my_app" in str(manager.config_dir.package_dir)
        assert "my_app" in str(manager.data.package_dir)
        assert "my_app" in str(manager.temp.package_dir)
        assert "my_app" in str(manager.logs.package_dir)

    def test_file_operations_in_managed_paths(self, temp_dir: Path) -> None:
        """Test actual file operations in managed paths."""
        config_content = f"""
[cache]
base_dir = "{temp_dir}/file_ops_cache"
package_dir = "{temp_dir}/file_ops_cache/{{package_name}}"

[data]
base_dir = "{temp_dir}/file_ops_data"
package_dir = "{temp_dir}/file_ops_data/{{package_name}}"
"""
        config_file = temp_dir / "file_ops_config.toml"
        config_file.write_text(config_content)

        manager = PathManager.for_package("file_test", config_file=config_file)

        # Test file operations in cache directory
        cache_file = manager.cache.package_dir / "test_cache.txt"
        cache_file.write_text("cached data")
        assert cache_file.exists()
        assert cache_file.read_text() == "cached data"

        # Test file operations in data directory
        data_file = manager.data.package_dir / "test_data.json"
        data_file.write_text('{"test": "data"}')
        assert data_file.exists()
        assert data_file.read_text() == '{"test": "data"}'

        # Test subdirectory creation
        subdir = manager.cache.package_dir / "subdir"
        subdir.mkdir()
        sub_file = subdir / "sub_file.txt"
        sub_file.write_text("subdirectory file")
        assert sub_file.exists()

    def test_multiple_package_isolation(self, temp_dir: Path) -> None:
        """Test that multiple packages have isolated paths."""
        config_content = f"""
[cache]
base_dir = "{temp_dir}/multi_cache"
package_dir = "{temp_dir}/multi_cache/{{package_name}}"

[data]
base_dir = "{temp_dir}/multi_data"
package_dir = "{temp_dir}/multi_data/{{package_name}}"
"""
        config_file = temp_dir / "multi_config.toml"
        config_file.write_text(config_content)

        # Create managers for different packages
        manager1 = PathManager.for_package("package1", config_file=config_file)
        manager2 = PathManager.for_package("package2", config_file=config_file)

        # Verify they share base directories
        assert manager1.cache.base_dir == manager2.cache.base_dir
        assert manager1.data.base_dir == manager2.data.base_dir

        # Verify they have separate package directories
        assert manager1.cache.package_dir != manager2.cache.package_dir
        assert manager1.data.package_dir != manager2.data.package_dir

        # Verify package names are in their respective paths
        assert "package1" in str(manager1.cache.package_dir)
        assert "package2" in str(manager2.cache.package_dir)
        assert "package1" not in str(manager2.cache.package_dir)
        assert "package2" not in str(manager1.cache.package_dir)

        # Test file isolation
        file1 = manager1.cache.package_dir / "data.txt"
        file2 = manager2.cache.package_dir / "data.txt"

        file1.write_text("package1 data")
        file2.write_text("package2 data")

        assert file1.read_text() == "package1 data"
        assert file2.read_text() == "package2 data"

    def test_default_config_behavior(self, mock_platformdirs: None) -> None:
        """Test behavior with default configuration."""
        manager = PathManager.for_package("default_test")

        # Verify default paths are created
        assert manager.cache.base_dir.exists()
        assert manager.cache.package_dir.exists()
        assert manager.config_dir.base_dir.exists()
        assert manager.config_dir.package_dir.exists()

        # Verify paths contain expected components
        assert "cache" in str(manager.cache.base_dir)
        assert "config" in str(manager.config_dir.base_dir)
        assert "data" in str(manager.data.base_dir)
        assert "twat" in str(manager.cache.base_dir)
        assert "default_test" in str(manager.cache.package_dir)

    def test_genai_paths_functionality(self, temp_dir: Path) -> None:
        """Test GenAI paths functionality."""
        config_content = f"""
[data]
base_dir = "{temp_dir}/genai_data"

[genai]
lora_dir = "{temp_dir}/genai_loras"
model_dir = "{temp_dir}/genai_models"
output_dir = "{temp_dir}/genai_output"
"""
        config_file = temp_dir / "genai_config.toml"
        config_file.write_text(config_content)

        manager = PathManager(config_file=config_file)

        # Test GenAI directory creation
        assert manager.genai.lora_dir.exists()
        assert manager.genai.model_dir.exists()
        assert manager.genai.output_dir.exists()

        # Test file operations in GenAI directories
        lora_file = manager.genai.lora_dir / "test_lora.safetensors"
        lora_file.write_text("lora data")
        assert lora_file.exists()

        model_file = manager.genai.model_dir / "test_model.ckpt"
        model_file.write_text("model data")
        assert model_file.exists()

        output_file = manager.genai.output_dir / "generated_image.png"
        output_file.write_text("image data")
        assert output_file.exists()

    def test_complex_environment_expansion(self, temp_dir: Path) -> None:
        """Test complex environment variable expansion."""
        base_path = temp_dir / "complex_env"
        app_name = "complex_app"

        with patch.dict(
            os.environ, {"APP_BASE": str(base_path), "APP_NAME": app_name, "USER_HOME": str(temp_dir / "home")}
        ):
            config_content = """
[cache]
base_dir = "${APP_BASE}/cache/${APP_NAME}"
package_dir = "${APP_BASE}/cache/${APP_NAME}/{package_name}"

[config]
base_dir = "${USER_HOME}/.config/${APP_NAME}"
package_dir = "${USER_HOME}/.config/${APP_NAME}/{package_name}"
"""
            config_file = temp_dir / "complex_config.toml"
            config_file.write_text(config_content)

            manager = PathManager.for_package("test_pkg", config_file=config_file)

            # Verify environment variables were expanded
            assert str(base_path) in str(manager.cache.base_dir)
            assert app_name in str(manager.cache.base_dir)
            assert str(temp_dir / "home") in str(manager.config_dir.base_dir)
            assert "test_pkg" in str(manager.cache.package_dir)
            assert "test_pkg" in str(manager.config_dir.package_dir)

    def test_get_path_integration(self, temp_dir: Path) -> None:
        """Test get_path method integration."""
        config_content = f"""
[cache]
base_dir = "{temp_dir}/get_path_cache"
package_dir = "{temp_dir}/get_path_cache/{{package_name}}"
"""
        config_file = temp_dir / "get_path_config.toml"
        config_file.write_text(config_content)

        manager = PathManager.for_package("get_path_test", config_file=config_file)

        # Test get_path with various configurations
        cache_base = manager.get_path("cache", "base_dir")
        cache_package = manager.get_path("cache", "package_dir")

        assert cache_base.exists()
        assert cache_package.exists()
        assert cache_base == manager.cache.base_dir
        assert cache_package == manager.cache.package_dir

        # Test with GenAI paths
        lora_path = manager.get_path("genai", "lora_dir")
        model_path = manager.get_path("genai", "model_dir")

        assert lora_path.exists()
        assert model_path.exists()
        assert lora_path == manager.genai.lora_dir
        assert model_path == manager.genai.model_dir

    def test_no_directory_creation_integration(self, temp_dir: Path) -> None:
        """Test integration with directory creation disabled."""
        config_content = f"""
[cache]
base_dir = "{temp_dir}/no_create_cache"
package_dir = "{temp_dir}/no_create_cache/{{package_name}}"
"""
        config_file = temp_dir / "no_create_config.toml"
        config_file.write_text(config_content)

        manager = PathManager.for_package("no_create_test", config_file=config_file, create_dirs=False)

        # Verify directories were not created
        assert not manager.cache.base_dir.exists()
        assert not manager.cache.package_dir.exists()

        # But we can still access the paths
        assert isinstance(manager.cache.base_dir, Path)
        assert isinstance(manager.cache.package_dir, Path)
        assert "no_create_test" in str(manager.cache.package_dir)
