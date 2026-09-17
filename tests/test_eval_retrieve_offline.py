"""Offline fixture mode for eval_retrieve.py. Must not read .env or open sockets."""
import json
import os
import subprocess
import sys

from kb_paths import repo_root


def test_offline_eval_writes_report(tmp_path):
    root = repo_root()
    fixture = root / "tests" / "fixtures" / "fake_retrieve.json"
    assert fixture.is_file()
    tracked_report = (root / "eval" / "last_report.md").read_text(encoding="utf-8")
    tracked_cache = (root / "eval" / "last_retrieve.json").read_text(encoding="utf-8")
    env = {k: v for k, v in os.environ.items()}
    env["EVAL_OUT_DIR"] = str(tmp_path)
    env["EVAL_NO_DOTENV"] = "1"
    proc = subprocess.run(
        [sys.executable, str(root / "scripts" / "eval_retrieve.py"), "--fixture", str(fixture)],
        cwd=root,
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    report = (tmp_path / "last_report.md").read_text(encoding="utf-8")
    assert "Recall@5" in report
    cache = json.loads((tmp_path / "last_retrieve.json").read_text(encoding="utf-8"))
    assert cache["items"]
    assert (root / "eval" / "last_report.md").read_text(encoding="utf-8") == tracked_report
    assert (root / "eval" / "last_retrieve.json").read_text(encoding="utf-8") == tracked_cache


def test_offline_eval_missing_env_exits_2(tmp_path):
    root = repo_root()
    env = {k: v for k, v in os.environ.items()
           if k not in ("RETRIEVE_API_KEY", "RETRIEVE_WORKSPACE_ID", "RETRIEVE_INDEX_ID")}
    env["EVAL_NO_DOTENV"] = "1"
    env["EVAL_OUT_DIR"] = str(tmp_path)
    proc = subprocess.run(
        [sys.executable, str(root / "scripts" / "eval_retrieve.py")],
        cwd=root,
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 2, proc.stderr + proc.stdout
