---
layout: default
title: Usage Guide
nav_order: 3
---

# Usage Guide

## Basic path resolution

```python
from twat_os import PathManager

pm = PathManager(create_dirs=False)  # don't create dirs yet
print(pm.cache.base_dir)       # Path object, platform-specific
print(pm.data.base_dir)
print(pm.logs.base_dir)
```

## Plugin-scoped paths

```python
pm = PathManager.for_package("my_twat_plugin")

# Directories are created automatically (create_dirs=True by default)
config_file = pm.config_dir.package_dir / "settings.toml"
cache_db    = pm.cache.package_dir      / "index.db"
log_file    = pm.logs.package_dir       / "run.log"
```

## GenAI asset paths

```python
pm = PathManager()

# Where to store downloaded model weights
weights = pm.genai.model_dir / "stable-diffusion-xl.safetensors"

# Where to store LoRA checkpoints
lora = pm.genai.lora_dir / "my_lora.pt"

# Where generated images land
output = pm.genai.output_dir / "generated_001.png"
```

## Custom TOML configuration

Create a `paths.toml` file to override any subset of paths:

```toml
[cache]
base_dir    = "/mnt/fast-ssd/my_app_cache"
package_dir = "/mnt/fast-ssd/my_app_cache/{package_name}"

[genai]
lora_dir   = "/mnt/fast-ssd/loras"
model_dir  = "/mnt/fast-ssd/models"
output_dir = "~/Pictures/ai_outputs"
```

Then pass the path to `PathManager`:

```python
pm = PathManager(package_name="my_plugin", config_file="paths.toml")
```

Only the sections you provide are overridden — all others fall back to the
platform defaults from `DEFAULT_PATHS`.

## Accessing a path by name

```python
pm = PathManager()
p = pm.get_path("cache", "base_dir")   # Path object
p = pm.get_path("genai", "lora_dir")  # Path object
```

## Environment variables and home expansion

Both `~` and `$VAR` / `${VAR}` are expanded in config file values:

```toml
[cache]
base_dir = "${XDG_CACHE_HOME}/twat"  # or "~/.cache/twat"
```

## CLI reference

```
# Resolve all paths (no directory creation)
twat-os paths --create=False

# Show paths for a specific plugin
twat-os paths --package=my_plugin

# Summary count
twat-os info --package=my_plugin

# Clipboard
twat-os clipboard

# Open a directory in the default file manager
twat-os open ~/.cache/twat
```

## Role in the twat ecosystem

`twat-os` registers itself as the `os` entry-point under `twat.plugins`:

```toml
[project.entry-points."twat.plugins"]
os = "twat_os"
```

Other `twat` plugins can therefore resolve OS paths through the shared
`PathManager` without duplicating platform-detection logic.
