---
layout: default
title: twat-os
nav_order: 1
---

# twat-os

**OS-aware path management for the twat ecosystem.**

`twat-os` is a `twat` plugin that resolves the correct platform-specific directories (cache, config, data, temp, logs, GenAI assets) at runtime using [`platformdirs`](https://platformdirs.readthedocs.io), then exposes them through typed Pydantic models.

## Why twat-os?

Every OS stores application data differently:

| Category | Linux | macOS | Windows |
|---|---|---|---|
| Cache | `~/.cache/twat` | `~/Library/Caches/twat` | `%LOCALAPPDATA%\twat\Cache` |
| Config | `~/.config/twat` | `~/Library/Preferences/twat` | `%APPDATA%\twat` |
| Data | `~/.local/share/twat` | `~/Library/Application Support/twat` | `%APPDATA%\twat` |
| Temp | runtime dir | `$TMPDIR/twat` | `%TEMP%\twat` |
| Logs | `~/.local/state/twat/logs` | `~/Library/Logs/twat` | `%APPDATA%\twat\Logs` |

Hard-coding any of these paths breaks cross-platform portability. `twat-os` makes every path available through a single call.

## Quick start

```python
from twat_os import PathManager

# Application-level paths (all categories)
pm = PathManager()
pm.cache.base_dir      # e.g. /home/user/.cache/twat
pm.config_dir.base_dir # e.g. /home/user/.config/twat
pm.data.base_dir       # e.g. /home/user/.local/share/twat
pm.logs.base_dir       # e.g. /home/user/.local/state/twat/logs

# Plugin-scoped paths — directories are created automatically
pm = PathManager.for_package("my_plugin")
pm.cache.package_dir   # .cache/twat/my_plugin
pm.data.package_dir    # .local/share/twat/my_plugin

# GenAI paths (models, LoRAs, outputs)
pm.genai.model_dir     # .local/share/twat/genai/models
pm.genai.lora_dir      # .local/share/twat/genai/loras
pm.genai.output_dir    # ~/Pictures/twat_genai
```

## CLI

```
twat-os version          # installed version
twat-os paths            # list all resolved paths
twat-os info             # summary (total / existing paths)
twat-os clipboard        # read system clipboard
twat-os open <path>      # open path with default app
```

## See also

- [API reference](api.md)
- [Usage guide](usage.md)
- [GitHub repository](https://github.com/twardoch/twat-os)
