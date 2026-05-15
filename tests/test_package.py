"""Test suite for twat_os."""

import pytest

import twat_os


def test_version() -> None:
    """Verify package exposes version."""
    assert twat_os.__version__


def test_public_exports_import() -> None:
    """Every public export listed in __all__ is importable from twat_os."""
    for name in twat_os.__all__:
        assert getattr(twat_os, name) is not None


def test_main_delegates_to_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    """The plugin-level main delegates to the real Fire CLI."""
    called = False

    def fake_cli_main() -> None:
        nonlocal called
        called = True

    monkeypatch.setattr("twat_os.__main__.main", fake_cli_main)

    twat_os.main()

    assert called
