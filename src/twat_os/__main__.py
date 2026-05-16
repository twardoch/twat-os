# this_file: src/twat_os/__main__.py
"""Fire CLI entry point for twat-os."""

from __future__ import annotations

import fire


def _version() -> str:
    """Print the installed twat-os version."""
    from twat_os.__version__ import __version__

    return __version__


def _paths(
    package: str | None = None,
    config: str | None = None,
    create: bool = True,
) -> dict:
    """Show all configured OS paths (cache, config, data, temp, logs, genai).

    Args:
        package: Package name for package-specific sub-paths.
        config: Path to a custom TOML configuration file.
        create: Create missing directories automatically.
    """
    from twat_os.paths import PathManager

    manager = PathManager(package_name=package, config_file=config, create_dirs=create)
    result: dict = {}
    for category in ["cache", "config_dir", "data", "temp", "logs"]:
        cfg = getattr(manager, category)
        result[category] = {
            "base_dir": str(cfg.base_dir),
            "exists": cfg.base_dir.exists(),
        }
        if cfg.package_dir:
            result[category]["package_dir"] = str(cfg.package_dir)
            result[category]["package_dir_exists"] = cfg.package_dir.exists()
    result["genai"] = {
        "base_dir": str(manager.genai.base_dir),
        "lora_dir": str(manager.genai.lora_dir),
        "model_dir": str(manager.genai.model_dir),
        "output_dir": str(manager.genai.output_dir),
    }
    return result


def _clipboard() -> str:
    """Read text from the system clipboard."""
    try:
        import subprocess

        import sys

        if sys.platform == "darwin":
            return subprocess.check_output(["pbpaste"], text=True)
        if sys.platform.startswith("linux"):
            return subprocess.check_output(["xclip", "-selection", "clipboard", "-o"], text=True)
        if sys.platform == "win32":
            import tkinter as tk

            root = tk.Tk()
            root.withdraw()
            return root.clipboard_get()
    except Exception as exc:
        return f"Error reading clipboard: {exc}"
    return ""


def _open(path: str) -> str:
    """Open PATH with the system default application."""
    import subprocess
    import sys
    from pathlib import Path

    resolved = Path(path).expanduser().resolve()
    if sys.platform == "darwin":
        subprocess.run(["open", str(resolved)], check=True)
    elif sys.platform.startswith("linux"):
        subprocess.run(["xdg-open", str(resolved)], check=True)
    elif sys.platform == "win32":
        subprocess.run(["start", str(resolved)], shell=True, check=True)
    return str(resolved)


def _info(package: str | None = None) -> dict:
    """Show twat-os path manager summary information.

    Args:
        package: Optional package name for package-specific paths.
    """
    from twat_os.paths import PathManager

    manager = PathManager(package_name=package, create_dirs=False)
    total = 0
    existing = 0
    for category in ["cache", "config_dir", "data", "temp", "logs"]:
        cfg = getattr(manager, category)
        total += 1
        if cfg.base_dir.exists():
            existing += 1
        if cfg.package_dir:
            total += 1
            if cfg.package_dir.exists():
                existing += 1
    for attr in ["base_dir", "lora_dir", "model_dir", "output_dir"]:
        total += 1
        if getattr(manager.genai, attr).exists():
            existing += 1
    return {
        "package": package,
        "total_paths": total,
        "existing_paths": existing,
        "missing_paths": total - existing,
    }


COMMANDS: dict[str, object] = {
    "version": _version,
    "paths": _paths,
    "clipboard": _clipboard,
    "open": _open,
    "info": _info,
}


def main() -> None:
    """twat-os: OS-aware path management and utilities."""
    fire.Fire(COMMANDS, name="twat-os")


def cmd_version() -> None:
    """twat-os version."""
    fire.Fire(_version, name="twat-os-version")


def cmd_paths() -> None:
    """Show all configured OS paths."""
    fire.Fire(_paths, name="twat-os-paths")


def cmd_clipboard() -> None:
    """Read text from the system clipboard."""
    fire.Fire(_clipboard, name="twat-os-clipboard")


def cmd_open() -> None:
    """Open a path with the system default application."""
    fire.Fire(_open, name="twat-os-open")


def cmd_info() -> None:
    """Show twat-os path manager summary information."""
    fire.Fire(_info, name="twat-os-info")


if __name__ == "__main__":
    main()
