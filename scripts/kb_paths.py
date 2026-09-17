"""Repo location helpers. Does not read .env or call retrieve."""
from __future__ import annotations

import subprocess
from pathlib import Path


def repo_root() -> Path:
    """Return rag-doc-eval root (parent of scripts/)."""
    return Path(__file__).resolve().parent.parent


def git_short_hash() -> str:
    """Return `git rev-parse --short HEAD`, or ``nogit`` if git is unavailable."""
    root = repo_root()
    proc = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return "nogit"
    return proc.stdout.strip() or "nogit"
