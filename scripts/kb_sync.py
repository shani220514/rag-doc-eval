"""kb_sync.py — sync CLI (guard + dry-run).

--dry-run: print `<rel_posix> <sha256>` per uploadable markdown, exit 0, no network.
Live (no --dry-run): requires RETRIEVE_ACCESS_KEY_ID/SECRET; otherwise exit 2
without network. v1 live upsert is a stub (exit 2).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kb_paths import repo_root  # noqa: E402
from sync_guard import SyncGuardError, assert_uploadable  # noqa: E402


def _iter_markdown(root: Path):
    for sub in ("cards", "sources"):
        base = root / sub
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.md")):
            rel = p.relative_to(root).as_posix()
            yield p, rel


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def upsert_markdown(rel_posix: str, body: str) -> str:
    """v1: not wired. Tests only exercise --dry-run."""
    raise NotImplementedError("live upsert is not implemented in v1")


def _dry_run(root: Path) -> int:
    count = 0
    for path, rel in _iter_markdown(root):
        body = path.read_text(encoding="utf-8")
        assert_uploadable(rel, body)
        digest = _sha256_file(path)
        print(f"{rel} {digest}")
        count += 1
    if count == 0:
        print("# no markdown files under cards/ or sources/", file=sys.stderr)
    return 0


def _live(root: Path) -> int:
    ak_id = os.environ.get("RETRIEVE_ACCESS_KEY_ID", "").strip()
    ak_secret = os.environ.get("RETRIEVE_ACCESS_KEY_SECRET", "").strip()
    if not ak_id or not ak_secret:
        print(
            "kb_sync: live mode requires RETRIEVE_ACCESS_KEY_ID and "
            "RETRIEVE_ACCESS_KEY_SECRET (or pass --dry-run)",
            file=sys.stderr,
        )
        return 2

    print(
        "kb_sync: live upsert not implemented in v1 (dry-run is the tested path)",
        file=sys.stderr,
    )
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sync cards/ and sources/ markdown (dry-run lists sha256).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List relative paths and sha256, write nothing remote, do not call eval_retrieve.",
    )
    args = parser.parse_args(argv)
    root = repo_root()

    if args.dry_run:
        try:
            return _dry_run(root)
        except SyncGuardError as e:
            print(f"kb_sync: upload blocked: {e}", file=sys.stderr)
            return 2

    return _live(root)


if __name__ == "__main__":
    raise SystemExit(main())
