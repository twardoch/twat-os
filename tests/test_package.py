"""Test suite for twat_os."""

import twat_os


def test_version() -> None:
    """Verify package exposes version."""
    assert twat_os.__version__
