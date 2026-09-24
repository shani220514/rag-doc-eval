"""eval_generate.py — 根据 Top5 写短答，再用规则打分。不用模型当裁判。

--answers：题目 id → 短答。有这个文件就用它，忽略 --model / --temperature，不读 .env、不发请求。
--model / --temperature：没有答案文件时，用模型按该题 Top5 写短答。需要 GENERATE_API_KEY。
两者都没给，或模型模式缺密钥：退出码 2，不发请求。
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from pathlib import Path
from typing import Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from eval_scoring import concat_top5  # noqa: E402
from kb_paths import git_short_hash, repo_root  # noqa: E402
from path_extract import extract_paths  # noqa: E402

DEFAULT_GENERATE_URL = (
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
)
_HTTP_TIMEOUT = 60


def score_answer(golden: dict, answer: str | None, chunks: list[dict]) -> dict:
    """短答要含全部 must_hit；抽出的 /v1/ 路径必须出现在这题 Top5 正文里。"""
    gid = str(golden.get("id") or "")
    intent = str(golden.get("intent") or "")
    must_hit = list(golden.get("must_hit") or [])
    text = "" if answer is None else str(answer)
    row = {
        "id": gid,
        "intent": intent,
        "had_must_hit": bool(must_hit),
        "extracted_paths": [],
        "illegal_paths": [],
        "answer": text,
    }
    if not text.strip():
        row["primary"] = "generate_error"
        row["tags"] = ["generate_error"]
        return row

    blob = concat_top5(chunks)
    tags: list[str] = []
    if must_hit and any(needle not in text for needle in must_hit):
        tags.append("answer_miss")
    paths = extract_paths(text)
    illegal = [p for p in paths if p not in blob]
    if illegal:
        tags.append("answer_path_hallucination")

    if "answer_miss" in tags:
        primary = "answer_miss"
    elif "answer_path_hallucination" in tags:
        primary = "answer_path_hallucination"
    else:
        primary = "ok"
    row["primary"] = primary
    row["tags"] = tags
    row["extracted_paths"] = paths
    row["illegal_paths"] = illegal
    return row


def aggregate_generate(rows: list[dict]) -> dict:
    """答案命中率 = 未 answer_miss 的题 / 带 must_hit 的有效题。路径幻觉看短答里的路径。"""
    effective = [r for r in rows if r.get("primary") != "generate_error"]
    hit_pool = [r for r in effective if r.get("had_must_hit")]
    hit_num = sum(1 for r in hit_pool if "answer_miss" not in r.get("tags", []))
    answer_hit = 1.0 if not hit_pool else hit_num / len(hit_pool)
    extracted_n = 0
    illegal_n = 0
    for r in effective:
        illegal = set(r.get("illegal_paths") or [])
        for p in r.get("extracted_paths") or []:
            extracted_n += 1
            if p in illegal:
                illegal_n += 1
    halluc = 0.0 if extracted_n == 0 else illegal_n / extracted_n
    return {
        "answer_hit": answer_hit,
        "halluc_rate": halluc,
        "n_effective": len(effective),
        "n_generate_error": len(rows) - len(effective),
        "n_extracted_paths": extracted_n,
        "n_illegal_paths": illegal_n,
    }


def gate_generate(current: dict) -> tuple[bool, list[str]]:
    """有效题为 0 必失败。答案命中率 ≥ 80%，答案路径幻觉率 ≤ 5%。"""
    reasons: list[str] = []
    if current.get("n_effective", 0) == 0:
        reasons.append("no effective answers (all generate_error or empty)")
        return False, reasons
    if current["answer_hit"] < 0.80:
        reasons.append("answer hit rate < 80%")
    if current["halluc_rate"] > 0.05:
        reasons.append("answer path hallucination rate > 5%")
    return (not reasons, reasons)


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def render_generate_report(
    *,
    git_hash: str,
    started_at: str,
    answer_source: str,
    model: str,
    temperature: float | None,
    metrics: dict,
    gate_ok: bool,
    gate_reasons: list[str],
    rows: list[dict],
) -> str:
    """生成报告与检索报告分开。答案来自文件时不写入模型名。"""
    lines = [
        "# RAG generate report",
        "",
        f"- git: {git_hash}",
        f"- started_at: {started_at}",
        f"- answer_source: {answer_source}",
        f"- generate_error: {metrics.get('n_generate_error', 0)}",
        f"- gate_ok: {gate_ok}",
    ]
    if answer_source == "model":
        lines.append(f"- model: {model}")
        if temperature is not None:
            lines.append(f"- temperature: {temperature}")
    if gate_reasons:
        lines.append(f"- gate_reasons: {'; '.join(gate_reasons)}")
    lines += [
        "",
        "| metric | current | gate |",
        "|--------|---------|------|",
        f"| 答案命中率 | {_pct(metrics['answer_hit'])} | ≥ 80% |",
        f"| 答案路径幻觉率 | {_pct(metrics['halluc_rate'])} | ≤ 5% |",
        "",
        "## items",
        "",
        "| id | intent | primary | tags | paths |",
        "|----|--------|---------|------|-------|",
    ]
    for r in rows:
        tags = ",".join(r.get("tags") or [])
        paths = " ".join(r.get("extracted_paths") or [])
        lines.append(
            f"| {r.get('id')} | {r.get('intent')} | {r.get('primary')} | {tags} | {paths} |"
        )
    return "\n".join(lines) + "\n"


def build_prompt(question: str, chunks: list[dict]) -> str:
    """让模型只根据这题 Top5 作答，并引用原文。"""
    blob = concat_top5(chunks)
    return (
        "只根据下面的段落回答问题。答案必须引用段落中的原文，"
        "不要写出段落里没有的 /v1/ 路径。\n\n"
        f"问题：{question}\n\n段落：\n{blob}"
    )


def parse_generation_body(payload: Mapping) -> str:
    """兼容 DashScope：output.text，或 output.choices[0].message.content。"""
    output = payload.get("output") if isinstance(payload, Mapping) else None
    if not isinstance(output, Mapping):
        return ""
    text = output.get("text")
    if isinstance(text, str) and text.strip():
        return text
    choices = output.get("choices")
    if isinstance(choices, list) and choices and isinstance(choices[0], Mapping):
        message = choices[0].get("message")
        if isinstance(message, Mapping):
            content = message.get("content")
            if isinstance(content, str):
                return content
    return ""


def _real_post_json(url: str, body: Mapping, headers: Mapping) -> tuple[int, Mapping]:
    req = Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=_HTTP_TIMEOUT) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode("utf-8")) or {}
        except Exception:
            payload = {"message": str(exc)}
        return exc.code, payload
    except URLError as exc:
        return 599, {"message": str(exc)}


def generate_answer(
    question: str,
    chunks: list[dict],
    *,
    model: str,
    temperature: float,
    api_key: str,
    post_json: Callable[[str, Mapping, Mapping], tuple[int, Mapping]],
    url: str = DEFAULT_GENERATE_URL,
) -> str:
    """按模型参数写一条短答。HTTP 失败或空正文返回空串，由打分记 generate_error。"""
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    body = {
        "model": model,
        "input": {
            "messages": [
                {"role": "user", "content": build_prompt(question, chunks)},
            ]
        },
        "parameters": {
            "temperature": temperature,
            "result_format": "message",
        },
    }
    status, payload = post_json(url, body, headers)
    if status not in (200, 201) or not isinstance(payload, Mapping):
        return ""
    return parse_generation_body(payload)


def _load_goldens(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    goldens = data.get("goldens") or []
    if not goldens:
        raise SystemExit(f"no goldens found in {path}")
    return goldens


def _load_json_object(path: Path, kind: str) -> dict:
    if not path.is_file():
        raise SystemExit(f"{kind} not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{kind} must be a JSON object: {path}")
    return data


def _chunks_from_fixture(fixture: dict) -> dict[str, list[dict]]:
    """评测夹具是 id → chunks。last_retrieve.json 是 {items: [{id, chunks}]}。"""
    if "items" in fixture and isinstance(fixture["items"], list):
        out: dict[str, list[dict]] = {}
        for item in fixture["items"]:
            if isinstance(item, dict) and item.get("id"):
                out[str(item["id"])] = list(item.get("chunks") or [])
        return out
    return {str(k): list(v or []) for k, v in fixture.items()}


def run_generate(
    root: Path,
    *,
    goldens: list[dict],
    fixture: dict,
    answers: dict | None,
    model: str | None,
    temperature: float | None,
    post_json: Callable[[str, Mapping, Mapping], tuple[int, Mapping]] | None,
    out_dir: Path,
    generate_url: str = DEFAULT_GENERATE_URL,
) -> int:
    """0 门禁通过，1 打分完成但未过，2 无法开跑（没给答案来源或模型缺密钥）。"""
    if answers is None and not model:
        sys.stderr.write("eval_generate: pass --answers or --model\n")
        return 2

    use_answers = answers is not None
    api_key = ""
    used_temperature = temperature
    if not use_answers:
        if os.environ.get("EVAL_NO_DOTENV") is None:
            from eval_retrieve import load_dotenv

            load_dotenv()
        api_key = os.environ.get("GENERATE_API_KEY", "").strip()
        if not api_key:
            sys.stderr.write(
                "eval_generate: model mode requires GENERATE_API_KEY "
                "(or pass --answers)\n"
            )
            return 2
        if used_temperature is None:
            used_temperature = 0.0
        post_json = post_json or _real_post_json

    chunks_by_id = _chunks_from_fixture(fixture)
    answer_source = "answers" if use_answers else "model"
    rows: list[dict] = []
    for g in goldens:
        gid = str(g["id"])
        chunks = list(chunks_by_id.get(gid) or [])
        if use_answers:
            text = answers.get(gid) if answers else None
            if text is None:
                text = ""
        else:
            try:
                text = generate_answer(
                    str(g.get("question") or ""),
                    chunks,
                    model=model or "",
                    temperature=float(used_temperature or 0.0),
                    api_key=api_key,
                    post_json=post_json,
                    url=generate_url,
                )
            except Exception as exc:
                sys.stderr.write(f"generate_error for {gid}: {exc}\n")
                text = ""
            if not str(text).strip():
                sys.stderr.write(f"generate_error for {gid}: empty answer\n")
        rows.append(score_answer(g, text, chunks))

    metrics = aggregate_generate(rows)
    gate_ok, gate_reasons = gate_generate(metrics)
    started_at = _dt.datetime.now().astimezone().isoformat()
    report = render_generate_report(
        git_hash=git_short_hash(),
        started_at=started_at,
        answer_source=answer_source,
        model=model or "",
        temperature=used_temperature if not use_answers else None,
        metrics=metrics,
        gate_ok=gate_ok,
        gate_reasons=gate_reasons,
        rows=rows,
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "last_generate_report.md").write_text(report, encoding="utf-8")
    cache = {
        "answer_source": answer_source,
        "model": "" if use_answers else (model or ""),
        "temperature": None if use_answers else used_temperature,
        "items": [
            {"id": r["id"], "answer": r.get("answer") or "", "primary": r["primary"]}
            for r in rows
        ],
    }
    (out_dir / "last_generate.json").write_text(
        json.dumps(cache, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return 0 if gate_ok else 1


def main(argv: list[str] | None = None) -> int:
    """CLI：--answers 离线打分；否则 --model 与 --temperature 调用生成。"""
    parser = argparse.ArgumentParser(
        description="Score short answers against Top5. --answers wins over --model."
    )
    parser.add_argument(
        "--answers",
        type=Path,
        default=None,
        help="JSON object id -> answer text. Skips the model even if --model is set.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Live generation model name. Ignored when --answers is set.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Live generation temperature. Ignored when --answers is set. Default 0.0.",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        default=None,
        help="id -> chunks JSON, or a last_retrieve.json cache. Default: eval/last_retrieve.json.",
    )
    parser.add_argument(
        "--goldens",
        type=Path,
        default=None,
        help="Golden YAML. Default: eval/goldens.yaml.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Write last_generate_report.md here (overrides EVAL_OUT_DIR).",
    )
    parser.add_argument(
        "--generate-url",
        default=os.environ.get("GENERATE_URL", DEFAULT_GENERATE_URL),
        help="Generation endpoint (model mode).",
    )
    args = parser.parse_args(argv)

    if args.answers is None and not args.model:
        sys.stderr.write("eval_generate: pass --answers or --model\n")
        return 2

    root = repo_root()

    def _resolve(p: Path | None) -> Path | None:
        if p is None:
            return None
        return p if p.is_absolute() else root / p

    if args.answers is None and os.environ.get("EVAL_NO_DOTENV") is None:
        from eval_retrieve import load_dotenv

        load_dotenv()

    goldens_path = _resolve(args.goldens) or (root / "eval" / "goldens.yaml")
    fixture_path = _resolve(args.fixture) or (root / "eval" / "last_retrieve.json")
    answers_path = _resolve(args.answers)
    try:
        goldens = _load_goldens(goldens_path)
        fixture = _load_json_object(fixture_path, "fixture")
        answers = _load_json_object(answers_path, "answers") if answers_path else None
    except SystemExit as exc:
        sys.stderr.write(str(exc) + "\n")
        return 2

    out_dir = _resolve(args.out_dir)
    if out_dir is None:
        out_dir_env = os.environ.get("EVAL_OUT_DIR")
        out_dir = Path(out_dir_env) if out_dir_env else None
    if out_dir is None:
        out_dir = root / "eval"

    return run_generate(
        root,
        goldens=goldens,
        fixture=fixture,
        answers=answers,
        model=args.model,
        temperature=args.temperature,
        post_json=None,
        out_dir=out_dir,
        generate_url=args.generate_url,
    )


if __name__ == "__main__":
    raise SystemExit(main())
