from __future__ import annotations

import os
import re
import subprocess
import sys

from kb_paths import repo_root


def _run(args, *, env=None, cwd=None):
    root = repo_root()
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "kb_sync.py"), *args],
        cwd=cwd or root,
        capture_output=True,
        text=True,
        env=env,
    )


def test_dry_run_lists_markdown_and_exits_zero():
    proc = _run(["--dry-run"])
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert "cards/purchase-order.md" in proc.stdout
    assert "sources/api/list-orders.md" in proc.stdout
    hex64 = re.compile(r"\b[0-9a-f]{64}\b")
    matches = hex64.findall(proc.stdout)
    assert len(matches) >= 2, proc.stdout


def test_dry_run_does_not_call_eval_retrieve():
    proc = _run(["--dry-run"])
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert "eval_retrieve" not in proc.stdout
    assert "eval_retrieve" not in proc.stderr


def test_dry_run_lists_heading_chunks_not_whole_files_only():
    """每一节一行。采购卡按标题切开，接口说明保持一节。"""
    proc = _run(["--dry-run"])
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert "cards/purchase-order.md#列表接口" in proc.stdout
    assert "cards/purchase-order.md#导读" in proc.stdout
    assert "sources/api/list-orders.md#List purchase orders" in proc.stdout
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    # 1 张卡 7 节 + 4 份接口说明各 1 节。
    assert len(lines) >= 11, proc.stdout
    for line in lines:
        chunk_id, digest = line.rsplit(" ", 1)
        assert "#" in chunk_id, line
        assert re.fullmatch(r"[0-9a-f]{64}", digest), line


def test_dry_run_uses_forward_slash_rel_paths():
    proc = _run(["--dry-run"])
    assert proc.returncode == 0, proc.stderr + proc.stdout
    for line in proc.stdout.splitlines():
        if "cards" in line or "sources" in line:
            assert "\\" not in line, line


def test_live_without_ak_env_exits_2_no_network():
    env = {k: v for k, v in os.environ.items()
           if k not in ("RETRIEVE_ACCESS_KEY_ID", "RETRIEVE_ACCESS_KEY_SECRET")}
    proc = _run([], env=env)
    assert proc.returncode == 2, proc.stderr + proc.stdout
    assert "eval_retrieve" not in proc.stdout


def test_env_example_has_keys():
    root = repo_root()
    text = (root / "env.example").read_text(encoding="utf-8")
    for key in (
        "RETRIEVE_API_KEY",
        "RETRIEVE_WORKSPACE_ID",
        "RETRIEVE_INDEX_ID",
        "RETRIEVE_ACCESS_KEY_ID",
        "RETRIEVE_ACCESS_KEY_SECRET",
        "RETRIEVE_URL",
    ):
        assert key in text, key
    assert "dry-run" in text.lower()
