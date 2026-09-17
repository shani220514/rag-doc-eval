"""Refuse files outside cards/sources and bodies that look like secrets."""
from __future__ import annotations

import re

SECRET_PATTERNS = (
    "Bearer ",
    "password",
    "AKIA",
)


class SyncGuardError(ValueError):
    """Upload blocked. Caller must not call retrieve upsert."""


def is_sync_allowed(rel_posix: str) -> bool:
    """True only for cards/**/*.md or sources/**/*.md (forward slashes)."""
    if ".." in rel_posix.split("/"):
        return False
    if not rel_posix.endswith(".md"):
        return False
    return rel_posix.startswith("cards/") or rel_posix.startswith("sources/")


def find_secret_hits(text: str) -> list[str]:
    """Return which SECRET_PATTERNS appear as substrings (case-sensitive except password)."""
    hits: list[str] = []
    for pat in SECRET_PATTERNS:
        if pat == "password":
            if re.search(r"password", text, flags=re.IGNORECASE):
                hits.append(pat)
        elif pat in text:
            hits.append(pat)
    return hits


def assert_uploadable(rel_posix: str, text: str) -> None:
    """Raise SyncGuardError if path or body is not safe to upsert."""
    if not is_sync_allowed(rel_posix):
        raise SyncGuardError(f"not in sync allowlist: {rel_posix}")
    hits = find_secret_hits(text)
    if hits:
        raise SyncGuardError(f"secret pattern(s) {hits} in {rel_posix}")
