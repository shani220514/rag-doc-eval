"""生成环节：夹具短答或模型参数写答案，规则打分，不调用裁判模型。"""
import json
import os
import subprocess
import sys

import pytest

from eval_generate import gate_generate, run_generate, score_answer
from kb_paths import repo_root


def _g(**kwargs):
    base = {
        "id": "A-01",
        "intent": "A_penetrate",
        "question": "列表路径？",
        "must_hit": ["/v1/purchase-orders"],
        "must_not_hit": [],
    }
    base.update(kwargs)
    return base


def _chunks(content="/v1/purchase-orders 查询窗 ≤7 天"):
    return [{"file_name": "cards/purchase-order.md", "title": "列表接口", "content": content}]


def test_answer_ok_when_needles_and_paths_are_in_top5():
    """短答带上全部 must_hit，路径也在这题 Top5 里，记 ok。"""
    row = score_answer(_g(), "列表是 /v1/purchase-orders", _chunks())
    assert row["primary"] == "ok"
    assert row["tags"] == []


def test_answer_miss_when_needle_absent():
    """must_hit 没写进短答，主分类是 answer_miss。"""
    row = score_answer(_g(must_hit=["查询窗 ≤7 天"]), "没有提到窗口", _chunks())
    assert row["primary"] == "answer_miss"
    assert "answer_miss" in row["tags"]


def test_path_outside_top5_is_hallucination():
    """短答里的路径必须已经出现在这题 Top5 正文中。"""
    row = score_answer(
        _g(must_hit=["查询窗 ≤7 天"]),
        "查询窗 ≤7 天，详见 /v1/not-in-top5",
        _chunks(),
    )
    assert row["primary"] == "answer_path_hallucination"
    assert row["extracted_paths"] == ["/v1/not-in-top5"]


def test_miss_outranks_path_hallucination():
    """针没中、路径也不在 Top5 时，主分类仍是 answer_miss，路径标签保留。"""
    row = score_answer(_g(must_hit=["没有的针"]), "见 /v1/elsewhere", _chunks())
    assert row["primary"] == "answer_miss"
    assert "answer_path_hallucination" in row["tags"]


def test_empty_answer_is_generate_error():
    """没有短答时不判针，记 generate_error。"""
    row = score_answer(_g(), "", _chunks())
    assert row["primary"] == "generate_error"


def test_gate_fails_when_nothing_was_scored():
    """有效题为 0 时生成门禁失败。"""
    ok, reasons = gate_generate({"n_effective": 0, "answer_hit": 1.0, "halluc_rate": 0.0})
    assert ok is False
    assert reasons


def test_answers_file_beats_model_and_skips_http(tmp_path):
    """同时给 --answers 和 --model 时用文件里的短答，不发请求。"""
    root = repo_root()
    called = {"n": 0}

    def post_json(_url, _body, _headers):
        called["n"] += 1
        return 200, {"output": {"text": "should not be used"}}

    code = run_generate(
        root,
        goldens=[_g()],
        fixture={"A-01": _chunks()},
        answers={"A-01": "列表是 /v1/purchase-orders"},
        model="qwen-turbo",
        temperature=0.9,
        post_json=post_json,
        out_dir=tmp_path,
    )
    assert code == 0
    assert called["n"] == 0
    report = (tmp_path / "last_generate_report.md").read_text(encoding="utf-8")
    assert "answer_source: answers" in report
    assert "qwen-turbo" not in report


def test_model_request_carries_model_and_temperature(tmp_path, monkeypatch):
    """没给答案文件时，模型名和 temperature 要进请求体。"""
    root = repo_root()
    monkeypatch.setenv("GENERATE_API_KEY", "test-key")
    seen = {}

    def post_json(_url, body, headers):
        seen["body"] = body
        seen["headers"] = headers
        return 200, {"output": {"text": "列表是 /v1/purchase-orders"}}

    code = run_generate(
        root,
        goldens=[_g()],
        fixture={"A-01": _chunks()},
        answers=None,
        model="qwen-turbo",
        temperature=0.2,
        post_json=post_json,
        out_dir=tmp_path,
    )
    assert code == 0, seen
    assert seen["body"]["model"] == "qwen-turbo"
    assert seen["body"]["parameters"]["temperature"] == 0.2
    assert "列表路径？" in json.dumps(seen["body"], ensure_ascii=False)
    assert seen["headers"]["Authorization"] == "Bearer test-key"
    report = (tmp_path / "last_generate_report.md").read_text(encoding="utf-8")
    assert "answer_source: model" in report
    assert "qwen-turbo" in report


def test_model_without_key_exits_2(tmp_path, monkeypatch):
    """只有 --model、没有密钥时退出码 2，不发请求。"""
    monkeypatch.delenv("GENERATE_API_KEY", raising=False)
    monkeypatch.setenv("EVAL_NO_DOTENV", "1")
    root = repo_root()

    def post_json(_url, _body, _headers):
        raise AssertionError("must not call the model")

    code = run_generate(
        root,
        goldens=[_g()],
        fixture={"A-01": _chunks()},
        answers=None,
        model="qwen-turbo",
        temperature=0.0,
        post_json=post_json,
        out_dir=tmp_path,
    )
    assert code == 2
    assert not (tmp_path / "last_generate_report.md").exists()


def test_cli_requires_answers_or_model(tmp_path):
    """答案文件和模型参数都没给时，CLI 退出码 2。"""
    root = repo_root()
    env = {k: v for k, v in os.environ.items() if k != "GENERATE_API_KEY"}
    env["EVAL_NO_DOTENV"] = "1"
    env["EVAL_OUT_DIR"] = str(tmp_path)
    proc = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "eval_generate.py"),
            "--fixture",
            str(root / "tests" / "fixtures" / "fake_retrieve.json"),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 2, proc.stderr + proc.stdout


def test_cli_fixture_answers_pass(tmp_path):
    """正式夹具短答可离线通过生成门禁，且不改检索报告。"""
    root = repo_root()
    tracked = (root / "eval" / "last_report.md").read_text(encoding="utf-8")
    env = {k: v for k, v in os.environ.items()}
    env["EVAL_NO_DOTENV"] = "1"
    env["EVAL_OUT_DIR"] = str(tmp_path)
    proc = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "eval_generate.py"),
            "--fixture",
            str(root / "tests" / "fixtures" / "fake_retrieve.json"),
            "--answers",
            str(root / "tests" / "fixtures" / "fake_answers.json"),
            "--model",
            "should-not-matter",
            "--temperature",
            "0.8",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    report = (tmp_path / "last_generate_report.md").read_text(encoding="utf-8")
    assert "answer_source: answers" in report
    assert "should-not-matter" not in report
    assert (root / "eval" / "last_report.md").read_text(encoding="utf-8") == tracked
