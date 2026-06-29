---
layout: default
title: API Reference
nav_order: 2
---

# API Reference

## Module `twat_os.paths`

### `PathManager`

Central manager that resolves and (optionally) creates all platform-specific directories.

```python
class PathManager:
    def __init__(
        self,
        package_name: str | None = None,
        config_file: str | Path | None = None,
        *,
        create_dirs: bool = True,
    ) -> None: ...

    @classmethod
    def for_package(
        cls,
        package_name: str,
        config_file: str | Path | None = None,
        *,
        create_dirs: bool = True,
    ) -> PathManager: ...

    def get_path(self, category: str, key: str = "base_dir") -> Path: ...
```

**Attributes** (all `PathConfig` subclass instances):

| Attribute | Type | Description |
|---|---|---|
| `cache` | `CacheConfig` | User cache directory |
| `config_dir` | `ConfigDirConfig` | User configuration directory |
| `data` | `DataDirConfig` | Persistent user data directory |
| `temp` | `TempDirConfig` | Runtime / temporary files directory |
| `logs` | `LogConfig` | Log files directory |
| `genai` | `GenAIConfig` | GenAI asset directories (models, LoRAs, outputs) |

Each has `.base_dir: Path` and `.package_dir: Path | None` (set when `package_name` is given).

**Parameters**

- `package_name` — when set, populates `*.package_dir` as a sub-path of each `base_dir`.
- `config_file` — optional TOML file that overrides specific sections. Missing sections fall back to `DEFAULT_PATHS`. Must include a `[cache]` key at minimum if provided.
- `create_dirs` — when `True` (default) every resolved directory is created with `mkdir(parents=True, exist_ok=True)`.

---

### `PathConfig`

Base Pydantic model for a single path category.

```python
class PathConfig(BaseModel):
    base_dir: Path
    package_dir: Path | None = None
    create_if_missing: bool = True
```

`base_dir` and `package_dir` are expanded: `~` is replaced with the real home directory and `$VAR` / `${VAR}` environment variables are substituted.

---

### Concrete config classes

| Class | `base_dir` default (Linux example) |
|---|---|
| `CacheConfig` | `platformdirs.user_cache_dir() / "twat"` |
| `ConfigDirConfig` | `platformdirs.user_config_dir() / "twat"` |
| `DataDirConfig` | `platformdirs.user_data_dir() / "twat"` |
| `TempDirConfig` | `platformdirs.user_runtime_dir() / "twat"` |
| `LogConfig` | `platformdirs.user_state_dir() / "twat/logs"` |
| `GenAIConfig` | `platformdirs.user_data_dir() / "twat/genai"` |

`GenAIConfig` adds three extra `Path` fields:

| Field | Default |
|---|---|
| `lora_dir` | `user_data_dir / "twat/genai/loras"` |
| `model_dir` | `user_data_dir / "twat/genai/models"` |
| `output_dir` | `Path.home() / "Pictures/twat_genai"` |

---

### Module-level constants

```python
PATHS_TOML: Path   # path to the bundled paths.toml template
DEFAULT_PATHS: dict  # parsed content of paths.toml
```

---

## Module `twat_os.__main__`

CLI entry points (invoked via `twat-os <command>`):

| Function | Command | Description |
|---|---|---|
| `_version()` | `twat-os version` | Print installed version string |
| `_paths(package, config, create)` | `twat-os paths` | Print resolved paths as a dict |
| `_info(package)` | `twat-os info` | Print summary (total / existing path count) |
| `_clipboard()` | `twat-os clipboard` | Read text from the system clipboard |
| `_open(path)` | `twat-os open <path>` | Open `path` with the default OS application |
