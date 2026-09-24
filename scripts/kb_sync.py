"""kb_sync.py — 切片清单（dry-run）与尚未接通的上传。

--dry-run：先对整份 Markdown 做路径和密钥拦截，再按标题打印
``<chunk_id> <sha256>``，退出码 0，不联网。
chunk_id 形如 ``cards/purchase-order.md#列表接口``，sha256 是这一段正文的摘要。

不带 --dry-run：需要 RETRIEVE_ACCESS_KEY_ID / SECRET，否则退出码 2 且不联网。
密钥齐了也仍退出码 2：v1 的 live upsert 还没接真正上传。
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from chunk_md import split_markdown  # noqa: E402
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


def upsert_markdown(rel_posix: str, body: str) -> str:
    """v1 不上传。测试只走 --dry-run 的切片清单。"""
    raise NotImplementedError("live upsert is not implemented in v1")


def _dry_run(root: Path) -> int:
    """列出每一段，不发送。整文件先过 guard，密钥出现在任一节都会拦住该文件。"""
    count = 0
    for path, rel in _iter_markdown(root):
        body = path.read_text(encoding="utf-8")
        assert_uploadable(rel, body)
        for chunk in split_markdown(rel, body):
            # 最后一列是 sha256，chunk_id 里可以有空格（英文标题）。
            print(f"{chunk['chunk_id']} {chunk['sha256']}")
            count += 1
    if count == 0:
        print("# no markdown chunks under cards/ or sources/", file=sys.stderr)
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
        description="List heading chunks under cards/ and sources/ (dry-run). Live upsert is not implemented.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List chunk_id and sha256 per heading. No network, do not call eval_retrieve.",
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
