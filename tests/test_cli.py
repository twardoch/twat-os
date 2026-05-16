# this_file: tests/test_cli.py
"""CLI tests for twat-os Fire entry points."""

from __future__ import annotations

import subprocess
import sys


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "twat_os", *args],
        capture_output=True,
        text=True,
    )


def test_help_exits_zero():
    """twat-os --help should exit 0 and print help text."""
    result = _run("--help")
    assert result.returncode == 0, result.stderr
    help_text = result.stdout + result.stderr
    assert help_text, "Expected help text on stdout or stderr"
    assert "twat-os" in help_text or "COMMAND" in help_text


def test_version_subcommand():
    """twat-os version should print a semver string."""
    result = _run("version")
    assert result.returncode == 0, result.stderr
    out = result.stdout.strip()
    assert out, "Expected version string"
    parts = out.split(".")
    assert len(parts) >= 2, f"Unexpected version format: {out!r}"


def test_paths_help():
    """twat-os paths --help should exit 0."""
    result = _run("paths", "--help")
    assert result.returncode == 0, result.stderr


def test_info_help():
    """twat-os info --help should exit 0."""
    result = _run("info", "--help")
    assert result.returncode == 0, result.stderr


def test_clipboard_help():
    """twat-os clipboard --help should exit 0."""
    result = _run("clipboard", "--help")
    assert result.returncode == 0, result.stderr


def test_open_help():
    """twat-os open --help should exit 0."""
    result = _run("open", "--help")
    assert result.returncode == 0, result.stderr


def test_paths_basic():
    """twat-os paths should return path data."""
    result = _run("paths", "--create=False")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip(), "Expected path output"


def test_info_basic():
    """twat-os info should return summary dict."""
    result = _run("info")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip(), "Expected info output"
