"""DF-order sample: pass fixture clears the gate, fail fixture does not."""
from __future__ import annotations

import json
import os
import subprocess
import sys

import yaml
from eval_scoring import aggregate_metrics, count_illegal_paths, score_item
from kb_paths import repo_root
from path_extract import build_whitelist


SAMPLE = "eval/samples/df-order"


def _paths(fixture_name: str):
    root = repo_root()
    base = root / SAMPLE
    return root, base / "goldens.yaml", base / fixture_name


def _score(fixture_name: str):
    root, goldens_path, fixture_path = _paths(fixture_name)
    goldens = yaml.safe_load(goldens_path.read_text(encoding="utf-8"))["goldens"]
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    bodies = []
    for sub in ("cards", "sources"):
        for md in sorted((root / sub).rglob("*.md")):
            bodies.append(md.read_text(encoding="utf-8"))
    whitelist = build_whitelist(bodies)
    goldens_by_id = {g["id"]: g for g in goldens}
    rows = [score_item(g, list(fixture[g["id"]]), whitelist) for g in goldens]
    illegal_n, extracted_n = count_illegal_paths(rows, whitelist, goldens_by_id)
    return aggregate_metrics(rows, illegal_n, extracted_n)


def test_df_pass_fixture_clears_gate():
    m = _score("fake_retrieve.json")
    assert m["n_effective"] == 12
    assert m["n_must_hit"] == 12
    assert m["n_c"] == 4
    assert m["n_extracted_paths"] == 0
    assert m["recall"] == 1.0
    assert m["module_acc"] == 1.0
    assert m["halluc_rate"] == 0.0


def test_df_fail_fixture_misses_gate():
    m = _score("fake_retrieve_fail.json")
    assert m["n_effective"] == 12
    assert abs(m["recall"] - (7 / 12)) < 1e-9
    assert abs(m["module_acc"] - 0.25) < 1e-9
    assert m["n_illegal_paths"] == 3
    assert m["n_extracted_paths"] == 3
    assert m["halluc_rate"] == 1.0


def _run_cli(tmp_path, fixture_name: str):
    root, goldens_path, fixture_path = _paths(fixture_name)
    tracked = (root / "eval" / "last_report.md").read_text(encoding="utf-8")
    env = dict(os.environ)
    env["EVAL_NO_DOTENV"] = "1"
    proc = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "eval_retrieve.py"),
            "--goldens",
            str(goldens_path),
            "--fixture",
            str(fixture_path),
            "--out-dir",
            str(tmp_path),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        env=env,
    )
    report = (tmp_path / "last_report.md").read_text(encoding="utf-8")
    assert (root / "eval" / "last_report.md").read_text(encoding="utf-8") == tracked
    return proc.returncode, report


def test_df_pass_cli_exits_0(tmp_path):
    code, report = _run_cli(tmp_path, "fake_retrieve.json")
    assert code == 0, report
    assert "gate_ok: True" in report
    assert "| Recall@5 | 100.0%" in report


def test_df_fail_cli_exits_1(tmp_path):
    code, report = _run_cli(tmp_path, "fake_retrieve_fail.json")
    assert code == 1, report
    assert "gate_ok: False" in report
    assert "| Recall@5 | 58.3%" in report
    assert "| 模块准确率 | 25.0%" in report
    assert "| 幻觉路径率 | 100.0%" in report
