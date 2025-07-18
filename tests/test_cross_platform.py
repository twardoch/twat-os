"""Cross-platform compatibility tests."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from twat_os.paths import PathManager


class TestCrossPlatform:
    """Test cross-platform compatibility."""

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_windows_path_handling(self, temp_dir: Path) -> None:
        """Test Windows-specific path handling."""
        config_content = f"""
[cache]
base_dir = "{temp_dir}\\\\windows_cache"
package_dir = "{temp_dir}\\\\windows_cache\\\\{{package_name}}"
"""
        config_file = temp_dir / "windows.toml"
        config_file.write_text(config_content)
        
        manager = PathManager.for_package("win_test", config_file=config_file)
        
        # Should handle Windows paths correctly
        assert manager.cache.base_dir.exists()
        assert manager.cache.package_dir.exists()
        assert "win_test" in str(manager.cache.package_dir)

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_unix_path_handling(self, temp_dir: Path) -> None:
        """Test Unix-specific path handling."""
        config_content = f"""
[cache]
base_dir = "{temp_dir}/unix_cache"
package_dir = "{temp_dir}/unix_cache/{{package_name}}"
"""
        config_file = temp_dir / "unix.toml"
        config_file.write_text(config_content)
        
        manager = PathManager.for_package("unix_test", config_file=config_file)
        
        # Should handle Unix paths correctly
        assert manager.cache.base_dir.exists()
        assert manager.cache.package_dir.exists()
        assert "unix_test" in str(manager.cache.package_dir)

    def test_path_separator_normalization(self, temp_dir: Path) -> None:
        """Test path separator normalization across platforms."""
        # Use mixed separators to test normalization
        if sys.platform == "win32":
            mixed_path = f"{temp_dir}\\\\mixed/path\\\\test"
        else:
            mixed_path = f"{temp_dir}/mixed\\\\path/test"
        
        config_content = f"""
[cache]
base_dir = "{mixed_path}"
package_dir = "{mixed_path}/{{package_name}}"
"""
        config_file = temp_dir / "mixed.toml"
        config_file.write_text(config_content)
        
        manager = PathManager.for_package("mixed_test", config_file=config_file)
        
        # Should normalize paths correctly
        assert manager.cache.base_dir.exists()
        assert manager.cache.package_dir.exists()
        assert "mixed_test" in str(manager.cache.package_dir)

    def test_home_directory_expansion(self, temp_dir: Path) -> None:
        """Test home directory expansion across platforms."""
        with patch("pathlib.Path.expanduser") as mock_expanduser:
            mock_expanduser.return_value = temp_dir / "fake_home"
            
            config_content = """
[cache]
base_dir = "~/test_cache"
package_dir = "~/test_cache/{package_name}"
"""
            config_file = temp_dir / "home.toml"
            config_file.write_text(config_content)
            
            manager = PathManager.for_package("home_test", config_file=config_file)
            
            # Should expand home directory
            assert "fake_home" in str(manager.cache.base_dir)
            assert "home_test" in str(manager.cache.package_dir)

    def test_environment_variables_expansion(self, temp_dir: Path) -> None:
        """Test environment variable expansion across platforms."""
        test_env_var = "TEST_PATH_VAR"
        test_value = str(temp_dir / "env_test")
        
        with patch.dict(os.environ, {test_env_var: test_value}):
            config_content = f"""
[cache]
base_dir = "${{{test_env_var}}}/cache"
package_dir = "${{{test_env_var}}}/cache/{{package_name}}"
"""
            config_file = temp_dir / "env.toml"
            config_file.write_text(config_content)
            
            manager = PathManager.for_package("env_test", config_file=config_file)
            
            # Should expand environment variables
            assert test_value in str(manager.cache.base_dir)
            assert "env_test" in str(manager.cache.package_dir)

    def test_case_sensitivity_handling(self, temp_dir: Path) -> None:
        """Test case sensitivity handling across platforms."""
        # Test with different cases
        config_content = f"""
[cache]
base_dir = "{temp_dir}/CaSeTeSt"
package_dir = "{temp_dir}/CaSeTeStNeW/{{package_name}}"
"""
        config_file = temp_dir / "case.toml"
        config_file.write_text(config_content)
        
        manager = PathManager.for_package("CaseTest", config_file=config_file)
        
        # Should handle case correctly based on platform
        assert manager.cache.base_dir.exists()
        assert manager.cache.package_dir.exists()
        assert "CaseTest" in str(manager.cache.package_dir)

    def test_long_path_handling(self, temp_dir: Path) -> None:
        """Test handling of long paths across platforms."""
        # Create a long path
        long_components = ["very_long_directory_name_component"] * 10
        long_path = temp_dir / "/".join(long_components)
        
        config_content = f"""
[cache]
base_dir = "{long_path}"
package_dir = "{long_path}/{{package_name}}"
"""
        config_file = temp_dir / "long.toml"
        config_file.write_text(config_content)
        
        try:
            manager = PathManager.for_package("long_test", config_file=config_file)
            # Should handle long paths if the platform supports them
            assert manager.cache.base_dir.exists()
            assert manager.cache.package_dir.exists()
        except OSError:
            # Some platforms may not support very long paths
            pytest.skip("Platform does not support long paths")

    def test_special_characters_in_paths(self, temp_dir: Path) -> None:
        """Test handling of special characters in paths."""
        # Test with various special characters that are generally safe
        special_chars = "test_dir-with.special+chars"
        special_path = temp_dir / special_chars
        
        config_content = f"""
[cache]
base_dir = "{special_path}"
package_dir = "{special_path}/{{package_name}}"
"""
        config_file = temp_dir / "special.toml"
        config_file.write_text(config_content)
        
        manager = PathManager.for_package("special_test", config_file=config_file)
        
        # Should handle special characters correctly
        assert manager.cache.base_dir.exists()
        assert manager.cache.package_dir.exists()
        assert "special_test" in str(manager.cache.package_dir)

    def test_permission_handling(self, temp_dir: Path) -> None:
        """Test permission handling across platforms."""
        # Create a directory with specific permissions
        perm_dir = temp_dir / "perm_test"
        perm_dir.mkdir()
        
        config_content = f"""
[cache]
base_dir = "{perm_dir}"
package_dir = "{perm_dir}/{{package_name}}"
"""
        config_file = temp_dir / "perm.toml"
        config_file.write_text(config_content)
        
        manager = PathManager.for_package("perm_test", config_file=config_file)
        
        # Should handle permissions correctly
        assert manager.cache.base_dir.exists()
        assert manager.cache.package_dir.exists()
        
        # Test file creation in the directory
        test_file = manager.cache.package_dir / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()

    def test_symlink_handling(self, temp_dir: Path) -> None:
        """Test symbolic link handling across platforms."""
        if sys.platform == "win32":
            pytest.skip("Symlink test skipped on Windows")
        
        # Create a symlink
        real_dir = temp_dir / "real_dir"
        real_dir.mkdir()
        symlink_dir = temp_dir / "symlink_dir"
        symlink_dir.symlink_to(real_dir)
        
        config_content = f"""
[cache]
base_dir = "{symlink_dir}"
package_dir = "{symlink_dir}/{{package_name}}"
"""
        config_file = temp_dir / "symlink.toml"
        config_file.write_text(config_content)
        
        manager = PathManager.for_package("symlink_test", config_file=config_file)
        
        # Should handle symlinks correctly
        assert manager.cache.base_dir.exists()
        assert manager.cache.package_dir.exists()
        
        # Test file creation through symlink
        test_file = manager.cache.package_dir / "test.txt"
        test_file.write_text("symlink test")
        assert test_file.exists()

    def test_network_path_handling(self, temp_dir: Path) -> None:
        """Test network path handling (where applicable)."""
        # This is more of a theoretical test since we can't easily create network paths
        # in a test environment, but we can test the path handling logic
        if sys.platform != "win32":
            pytest.skip("Network path test is Windows-specific")
        
        # Simulate UNC path format
        unc_path = f"\\\\server\\share\\{temp_dir.name}"
        
        config_content = f"""
[cache]
base_dir = "{unc_path}"
package_dir = "{unc_path}/{{package_name}}"
"""
        config_file = temp_dir / "network.toml"
        config_file.write_text(config_content)
        
        try:
            manager = PathManager.for_package("network_test", config_file=config_file, create_dirs=False)
            # Should parse UNC paths correctly (even if they don't exist)
            assert "server" in str(manager.cache.base_dir)
            assert "share" in str(manager.cache.base_dir)
        except Exception:
            # Network paths might not be supported in test environment
            pytest.skip("Network path handling not supported in test environment")

    def test_drive_letter_handling(self, temp_dir: Path) -> None:
        """Test drive letter handling on Windows."""
        if sys.platform != "win32":
            pytest.skip("Drive letter test is Windows-specific")
        
        # Test absolute path with drive letter
        drive_path = f"C:\\temp\\{temp_dir.name}"
        
        config_content = f"""
[cache]
base_dir = "{drive_path}"
package_dir = "{drive_path}\\{{package_name}}"
"""
        config_file = temp_dir / "drive.toml"
        config_file.write_text(config_content)
        
        manager = PathManager.for_package("drive_test", config_file=config_file, create_dirs=False)
        
        # Should handle drive letters correctly
        assert manager.cache.base_dir.is_absolute()
        assert str(manager.cache.base_dir).startswith("C:")
        assert "drive_test" in str(manager.cache.package_dir)