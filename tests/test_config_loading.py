"""Tests for configuration loading and validation."""

import tempfile
from pathlib import Path

import pytest
import tomli

from twat_os.paths import DEFAULT_PATHS, PATHS_TOML, PathManager


class TestConfigLoading:
    """Test configuration loading functionality."""

    def test_default_paths_loading(self) -> None:
        """Test that default paths are loaded correctly."""
        assert isinstance(DEFAULT_PATHS, dict)
        assert "cache" in DEFAULT_PATHS
        assert "config" in DEFAULT_PATHS
        assert "data" in DEFAULT_PATHS
        assert "temp" in DEFAULT_PATHS
        assert "genai" in DEFAULT_PATHS
        assert "logs" in DEFAULT_PATHS

    def test_paths_toml_file_exists(self) -> None:
        """Test that the paths.toml file exists."""
        assert PATHS_TOML.exists()
        assert PATHS_TOML.is_file()

    def test_paths_toml_valid_format(self) -> None:
        """Test that paths.toml is valid TOML format."""
        content = PATHS_TOML.read_text()
        parsed = tomli.loads(content)
        assert isinstance(parsed, dict)

    def test_paths_toml_required_sections(self) -> None:
        """Test that paths.toml contains required sections."""
        content = PATHS_TOML.read_text()
        parsed = tomli.loads(content)

        required_sections = ["cache", "config", "data", "temp", "genai", "logs"]
        for section in required_sections:
            assert section in parsed, f"Missing required section: {section}"

    def test_paths_toml_required_keys(self) -> None:
        """Test that paths.toml sections contain required keys."""
        content = PATHS_TOML.read_text()
        parsed = tomli.loads(content)

        # Standard sections should have base_dir and package_dir
        standard_sections = ["cache", "config", "data", "temp", "logs"]
        for section in standard_sections:
            assert "base_dir" in parsed[section], f"Missing base_dir in {section}"
            assert "package_dir" in parsed[section], f"Missing package_dir in {section}"

        # GenAI section should have specific keys
        genai_keys = ["lora_dir", "model_dir", "output_dir"]
        for key in genai_keys:
            assert key in parsed["genai"], f"Missing {key} in genai section"

    def test_custom_config_file_loading(self, temp_dir: Path) -> None:
        """Test loading custom configuration file."""
        custom_config = {
            "cache": {
                "base_dir": str(temp_dir / "custom_cache"),
                "package_dir": str(temp_dir / "custom_cache/{package_name}"),
            },
            "config": {
                "base_dir": str(temp_dir / "custom_config"),
                "package_dir": str(temp_dir / "custom_config/{package_name}"),
            },
            "data": {
                "base_dir": str(temp_dir / "custom_data"),
                "package_dir": str(temp_dir / "custom_data/{package_name}"),
            },
            "temp": {
                "base_dir": str(temp_dir / "custom_temp"),
                "package_dir": str(temp_dir / "custom_temp/{package_name}"),
            },
            "genai": {
                "lora_dir": str(temp_dir / "custom_genai/loras"),
                "model_dir": str(temp_dir / "custom_genai/models"),
                "output_dir": str(temp_dir / "custom_genai/output"),
            },
            "logs": {
                "base_dir": str(temp_dir / "custom_logs"),
                "package_dir": str(temp_dir / "custom_logs/{package_name}"),
            },
        }

        config_file = temp_dir / "custom.toml"
        config_content = ""
        for section, values in custom_config.items():
            config_content += f"[{section}]\n"
            for key, value in values.items():
                config_content += f'{key} = "{value}"\n'
            config_content += "\n"

        config_file.write_text(config_content)

        manager = PathManager(config_file=config_file, create_dirs=False)

        # Verify custom paths are used
        assert str(manager.cache.base_dir) == str(temp_dir / "custom_cache")
        assert str(manager.config_dir.base_dir) == str(temp_dir / "custom_config")
        assert str(manager.data.base_dir) == str(temp_dir / "custom_data")
        assert str(manager.temp.base_dir) == str(temp_dir / "custom_temp")
        assert str(manager.genai.lora_dir) == str(temp_dir / "custom_genai/loras")
        assert str(manager.genai.model_dir) == str(temp_dir / "custom_genai/models")
        assert str(manager.genai.output_dir) == str(temp_dir / "custom_genai/output")
        assert str(manager.logs.base_dir) == str(temp_dir / "custom_logs")

    def test_partial_config_override(self, temp_dir: Path) -> None:
        """Test partial configuration override."""
        # Only override cache configuration
        config_content = f"""
[cache]
base_dir = "{temp_dir}/partial_cache"
package_dir = "{temp_dir}/partial_cache/{{package_name}}"
"""
        config_file = temp_dir / "partial.toml"
        config_file.write_text(config_content)

        manager = PathManager(config_file=config_file, create_dirs=False)

        # Cache should use custom paths
        assert str(manager.cache.base_dir) == str(temp_dir / "partial_cache")

        # Other sections should use defaults
        assert "~/.config/twat" in str(manager.config_dir.base_dir) or "config" in str(manager.config_dir.base_dir)

    def test_invalid_toml_format(self, temp_dir: Path) -> None:
        """Test handling of invalid TOML format."""
        config_file = temp_dir / "invalid.toml"
        config_file.write_text("invalid toml content [[[")

        with pytest.raises(tomli.TOMLDecodeError):
            PathManager(config_file=config_file)

    def test_missing_required_section(self, temp_dir: Path) -> None:
        """Test handling of missing required sections."""
        # Config missing cache section
        config_content = """
[config]
base_dir = "/tmp/test"
package_dir = "/tmp/test/{package_name}"
"""
        config_file = temp_dir / "missing_section.toml"
        config_file.write_text(config_content)

        with pytest.raises(KeyError):
            PathManager(config_file=config_file)

    def test_missing_required_key(self, temp_dir: Path) -> None:
        """Test handling of missing required keys."""
        # Config missing base_dir in cache section
        config_content = """
[cache]
package_dir = "/tmp/test/{package_name}"
"""
        config_file = temp_dir / "missing_key.toml"
        config_file.write_text(config_content)

        with pytest.raises(KeyError):
            PathManager(config_file=config_file)

    def test_config_with_comments(self, temp_dir: Path) -> None:
        """Test configuration file with comments."""
        config_content = f"""
# This is a test configuration file
[cache]
# Base directory for cache
base_dir = "{temp_dir}/commented_cache"
# Package-specific cache directory
package_dir = "{temp_dir}/commented_cache/{{package_name}}"

[config]
# Configuration directory
base_dir = "{temp_dir}/commented_config"
package_dir = "{temp_dir}/commented_config/{{package_name}}"
"""
        config_file = temp_dir / "commented.toml"
        config_file.write_text(config_content)

        manager = PathManager(config_file=config_file, create_dirs=False)

        # Should work despite comments
        assert str(manager.cache.base_dir) == str(temp_dir / "commented_cache")
        assert str(manager.config_dir.base_dir) == str(temp_dir / "commented_config")

    def test_config_with_unicode_paths(self, temp_dir: Path) -> None:
        """Test configuration with Unicode characters in paths."""
        unicode_dir = temp_dir / "测试目录"
        config_content = f"""
[cache]
base_dir = "{unicode_dir}/缓存"
package_dir = "{unicode_dir}/缓存/{{package_name}}"
"""
        config_file = temp_dir / "unicode.toml"
        config_file.write_text(config_content, encoding="utf-8")

        manager = PathManager(config_file=config_file, create_dirs=False)

        # Should handle Unicode paths correctly
        assert "测试目录" in str(manager.cache.base_dir)
        assert "缓存" in str(manager.cache.base_dir)

    def test_config_with_spaces_in_paths(self, temp_dir: Path) -> None:
        """Test configuration with spaces in paths."""
        space_dir = temp_dir / "path with spaces"
        config_content = f"""
[cache]
base_dir = "{space_dir}/cache dir"
package_dir = "{space_dir}/cache dir/{{package_name}}"
"""
        config_file = temp_dir / "spaces.toml"
        config_file.write_text(config_content)

        manager = PathManager(config_file=config_file, create_dirs=False)

        # Should handle spaces in paths correctly
        assert "path with spaces" in str(manager.cache.base_dir)
        assert "cache dir" in str(manager.cache.base_dir)
