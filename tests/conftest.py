"""Test configuration and shared fixtures."""

import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config_content() -> str:
    """Sample TOML configuration content for testing."""
    return """
[cache]
base_dir = "/tmp/test_cache"
package_dir = "/tmp/test_cache/{package_name}"

[config]
base_dir = "/tmp/test_config"
package_dir = "/tmp/test_config/{package_name}"

[data]
base_dir = "/tmp/test_data"
package_dir = "/tmp/test_data/{package_name}"

[temp]
base_dir = "/tmp/test_temp"
package_dir = "/tmp/test_temp/{package_name}"

[genai]
lora_dir = "/tmp/test_genai/loras"
model_dir = "/tmp/test_genai/models"
output_dir = "/tmp/test_genai/output"

[logs]
base_dir = "/tmp/test_logs"
package_dir = "/tmp/test_logs/{package_name}"
"""


@pytest.fixture
def sample_config_file(temp_dir: Path, sample_config_content: str) -> Path:
    """Create a sample configuration file for testing."""
    config_file = temp_dir / "test_config.toml"
    config_file.write_text(sample_config_content)
    return config_file


@pytest.fixture
def mock_platformdirs(monkeypatch: pytest.MonkeyPatch, temp_dir: Path) -> None:
    """Mock platformdirs to use temporary directories."""
    import platformdirs
    
    test_base = temp_dir / "platformdirs"
    test_base.mkdir()
    
    monkeypatch.setattr(platformdirs, "user_cache_dir", lambda: str(test_base / "cache"))
    monkeypatch.setattr(platformdirs, "user_config_dir", lambda: str(test_base / "config"))
    monkeypatch.setattr(platformdirs, "user_data_dir", lambda: str(test_base / "data"))
    monkeypatch.setattr(platformdirs, "user_runtime_dir", lambda: str(test_base / "runtime"))
    monkeypatch.setattr(platformdirs, "user_state_dir", lambda: str(test_base / "state"))