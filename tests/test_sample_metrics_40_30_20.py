"""Sample goldens+fixture must score Recall@5=40%, module acc=30%, halluc=20%."""
import json
import os
import subprocess
import sys

import yaml
from eval_scoring import aggregate_metrics, count_illegal_paths, score_item
from kb_paths import repo_root
from path_extract import build_whitelist


SAMPLE = "eval/samples/metrics-40-30-20"


def _sample_paths():
    root = repo_root()
    base = root / SAMPLE
    return root, base / "goldens.yaml", base / "fake_retrieve.json"


def _score_sample():
    root, goldens_path, fixture_path = _sample_paths()
    goldens = yaml.safe_load(goldens_path.read_text(encoding="utf-8"))["goldens"]
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    bodies = []
    for sub in ("cards", "sources"):
        for md in sorted((root / sub).rglob("*.md")):
            bodies.append(md.read_text(encoding="utf-8"))
    whitelist = build_whitelist(bodies)
    goldens_by_id = {g["id"]: g for g in goldens}
    rows = [
        score_item(g, list(fixture[g["id"]]), whitelist)
        for g in goldens
    ]
    illegal_n, extracted_n = count_illegal_paths(rows, whitelist, goldens_by_id)
    metrics = aggregate_metrics(rows, illegal_n, extracted_n)
    return rows, metrics


def test_sample_metrics_are_40_30_20():
    _rows, m = _score_sample()
    assert m["n_effective"] == 15
    assert m["n_must_hit"] == 15
    assert m["n_c"] == 10
    assert m["n_extracted_paths"] == 15
    assert m["n_illegal_paths"] == 3
    assert abs(m["recall"] - 0.40) < 1e-9
    assert abs(m["module_acc"] - 0.30) < 1e-9
    assert abs(m["halluc_rate"] - 0.20) < 1e-9


def test_sample_cli_writes_failing_report(tmp_path):
    root, goldens_path, fixture_path = _sample_paths()
    tracked_report = (root / "eval" / "last_report.md").read_text(encoding="utf-8")
    env = {k: v for k, v in os.environ.items()}
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
    assert proc.returncode == 1, proc.stderr + proc.stdout
    report = (tmp_path / "last_report.md").read_text(encoding="utf-8")
    stamped = list(tmp_path.glob("last_report_*.md"))
    assert len(stamped) == 1, stamped
    assert stamped[0].read_text(encoding="utf-8") == report
    assert "| Recall@5 | 40.0%" in report
    assert "| 模块准确率 | 30.0%" in report
    assert "| 幻觉路径率 | 20.0%" in report
    assert "gate_ok: False" in report
    assert (root / "eval" / "last_report.md").read_text(encoding="utf-8") == tracked_report
