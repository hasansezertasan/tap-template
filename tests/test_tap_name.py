"""Tests for repository-to-tap name resolution."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import tap_name  # noqa: E402


class FromRemoteTest(unittest.TestCase):
    def test_https_homebrew_prefix(self) -> None:
        self.assertEqual(
            tap_name.from_remote("https://github.com/acme/homebrew-tools.git"),
            "acme/tools",
        )

    def test_ssh_homebrew_prefix(self) -> None:
        self.assertEqual(
            tap_name.from_remote("git@github.com:acme/homebrew-tools.git"),
            "acme/tools",
        )

    def test_repository_without_prefix(self) -> None:
        self.assertEqual(
            tap_name.from_remote("https://github.com/acme/tools.git"),
            "acme/tools",
        )

    def test_non_github_remote(self) -> None:
        self.assertIsNone(tap_name.from_remote("https://example.com/acme/tools.git"))


if __name__ == "__main__":
    unittest.main()
