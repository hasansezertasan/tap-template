"""Resolve the Homebrew tap name for this repository."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


def from_remote(remote: str) -> str | None:
    """Convert a GitHub remote URL to ``owner/tap`` notation."""
    match = re.search(r"github\.com[/:]([^/]+)/([^/#?]+?)(?:\.git)?$", remote.strip())
    if not match:
        return None
    owner, repository = match.groups()
    return f"{owner}/{repository.removeprefix('homebrew-')}"


def resolve(repo_root: Path) -> str | None:
    """Resolve a tap override or infer it from the ``origin`` remote."""
    if override := os.environ.get("HOMEBREW_TAP"):
        return override
    try:
        remote = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return from_remote(remote)
