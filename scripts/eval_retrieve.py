"""eval_retrieve.py — offline-first RAG retrieve evaluation CLI.

Fixture mode (--fixture): no .env, no network.
Live mode: requires RETRIEVE_API_KEY, RETRIEVE_WORKSPACE_ID, RETRIEVE_INDEX_ID.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
import time
from pathlib import Path
from typing import Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from eval_scoring import (  # noqa: E402
    aggregate_metrics,
    count_illegal_paths,
    gate_metrics,
    score_item,
)
from kb_paths import git_short_hash, repo_root  # noqa: E402
from path_extract import build_whitelist, whitelist_yaml  # noqa: E402
from report import render_last_report  # noqa: E402
from retrieve_client import RetrieveError, retrieve_top5  # noqa: E402

_LIVE_ENV_VARS = ("RETRIEVE_API_KEY", "RETRIEVE_WORKSPACE_ID", "RETRIEVE_INDEX_ID")
_HTTP_TIMEOUT = 30


def load_dotenv(env_path: Path | None = None) -> dict[str, str]:
    """Parse a ``.env`` file into ``os.environ``. Never called at import time."""
    if os.environ.get("EVAL_NO_DOTENV"):
        return {}
    if env_path is None:
        env_path = repo_root() / ".env"
    if not env_path.is_file():
        return {}
    loaded: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if "=" not in s:
            continue
        key, _, val = s.partition("=")
        key = key.strip()
        if not key:
            continue
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
            val = val[1:-1]
        if key not in os.environ:
            os.environ[key] = val
            loaded[key] = val
    return loaded


def _load_goldens(root: Path) -> list[dict]:
    path = root / "eval" / "goldens.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    goldens = data.get("goldens") or []
    if not goldens:
        raise SystemExit(f"no goldens found in {path}")
    return goldens


def _scan_markdown(root: Path) -> list[str]:
    bodies: list[str] = []
    for sub in ("cards", "sources"):
        base = root / sub
        if not base.is_dir():
            continue
        for md in sorted(base.rglob("*.md")):
            bodies.append(md.read_text(encoding="utf-8"))
    return bodies


def _write_whitelist_to(out_dir: Path, paths: list[str]) -> None:
    out = out_dir / "path_whitelist.yaml"
    out.write_text(whitelist_yaml(paths), encoding="utf-8")


def _load_fixture(fixture_path: Path) -> dict[str, list[dict]]:
    if not fixture_path.is_file():
        raise SystemExit(f"fixture not found: {fixture_path}")
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"fixture must be a JSON object id->chunks: {fixture_path}")
    return data


def parse_baseline_md(text: str) -> dict | None:
    """Extract the three percentages from baseline_report.md."""
    import re

    wanted = {"Recall@5": "recall", "模块准确率": "module_acc", "幻觉路径率": "halluc_rate"}
    out: dict[str, float] = {}
    for line in text.splitlines():
        m = re.match(r"\|\s*([^|]+?)\s*\|\s*([0-9]+(?:\.[0-9]+)?)\s*%\s*\|", line)
        if not m:
            continue
        key = m.group(1).strip()
        if key in wanted:
            out[wanted[key]] = float(m.group(2)) / 100.0
    if len(out) != 3:
        return None
    return out


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


def _retrieve_live(
    question: str,
    *,
    post_json: Callable[[str, Mapping, Mapping], tuple[int, Mapping]],
    sleep: Callable[[float], None],
    url: str,
    api_key: str,
    workspace_id: str,
    index_id: str,
) -> list[dict]:
    return retrieve_top5(
        question,
        post_json=post_json,
        sleep=sleep,
        url=url,
        api_key=api_key,
        workspace_id=workspace_id,
        pipeline_id=index_id,
    )


def run_eval(
    root: Path,
    *,
    fixture: dict | None,
    api_key: str | None,
    workspace_id: str | None,
    index_id: str | None,
    retrieve_url: str,
    post_json: Callable[[str, Mapping, Mapping], tuple[int, Mapping]] | None,
    sleep: Callable[[float], None] | None,
    out_dir: Path | None = None,
) -> int:
    eval_in = root / "eval"
    eval_out = out_dir if out_dir is not None else eval_in
    eval_out.mkdir(parents=True, exist_ok=True)

    goldens = _load_goldens(root)
    goldens_by_id = {g["id"]: g for g in goldens}

    bodies = _scan_markdown(root)
    whitelist = build_whitelist(bodies)
    _write_whitelist_to(eval_out, whitelist)

    live_mode = fixture is None
    if live_mode:
        missing = [v for v in _LIVE_ENV_VARS if not os.environ.get(v)]
        if missing:
            sys.stderr.write(
                "missing required env for live mode: " + ", ".join(missing) + "\n"
            )
            return 2
        api_key = os.environ["RETRIEVE_API_KEY"]
        workspace_id = os.environ["RETRIEVE_WORKSPACE_ID"]
        index_id = os.environ["RETRIEVE_INDEX_ID"]
        post_json = post_json or _real_post_json
        sleep = sleep or time.sleep

    git_hash = git_short_hash()
    if git_hash == "nogit":
        sys.stderr.write("warn: git hash unavailable\n")

    started_at = _dt.datetime.now().astimezone().isoformat()
    used_index_id = index_id or ""

    items: list[dict] = []
    rows: list[dict] = []
    for g in goldens:
        gid = g["id"]
        chunks: list[dict] = []
        retrieve_error = False
        try:
            if fixture is not None:
                chunks = list(fixture.get(gid) or [])
                if not chunks:
                    raise RetrieveError(f"fixture missing id {gid}")
            else:
                chunks = _retrieve_live(
                    g["question"],
                    post_json=post_json,
                    sleep=sleep,
                    url=retrieve_url,
                    api_key=api_key or "",
                    workspace_id=workspace_id or "",
                    index_id=used_index_id,
                )
        except RetrieveError as exc:
            retrieve_error = True
            sys.stderr.write(f"retrieve_error for {gid}: {exc}\n")

        row = score_item(g, chunks, whitelist, retrieve_error=retrieve_error)
        rows.append(row)
        items.append({"id": gid, "chunks": chunks})

    illegal_n, extracted_n = count_illegal_paths(rows, whitelist, goldens_by_id)
    metrics = aggregate_metrics(rows, illegal_n, extracted_n)

    baseline_path = eval_in / "baseline_report.md"
    baseline = None
    if baseline_path.is_file():
        baseline = parse_baseline_md(baseline_path.read_text(encoding="utf-8"))

    gate_ok, gate_reasons = gate_metrics(metrics, baseline)

    report_md = render_last_report(
        git_hash=git_hash,
        index_id=used_index_id,
        started_at=started_at,
        metrics=metrics,
        baseline=baseline,
        gate_ok=gate_ok,
        gate_reasons=gate_reasons,
        rows=rows,
    )
    (eval_out / "last_report.md").write_text(report_md, encoding="utf-8")

    cache = {
        "git": git_hash,
        "index_id": used_index_id,
        "items": items,
    }
    (eval_out / "last_retrieve.json").write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return 0 if gate_ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="RAG retrieve eval (fixture offline / live HTTP)"
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        default=None,
        help="Offline: read id->chunks JSON. No .env, no network.",
    )
    parser.add_argument(
        "--retrieve-url",
        default=os.environ.get(
            "RETRIEVE_URL",
            "https://dashscope.aliyuncs.com/api/v1/indices/retrieve",
        ),
        help="Retrieve endpoint (live mode)",
    )
    args = parser.parse_args(argv)

    root = repo_root()
    fixture = _load_fixture(args.fixture) if args.fixture else None

    if fixture is None:
        load_dotenv()

    out_dir_env = os.environ.get("EVAL_OUT_DIR")
    out_dir = Path(out_dir_env) if out_dir_env else None

    return run_eval(
        root,
        fixture=fixture,
        api_key=None,
        workspace_id=None,
        index_id=None,
        retrieve_url=args.retrieve_url,
        post_json=None,
        sleep=None,
        out_dir=out_dir,
    )


if __name__ == "__main__":
    sys.exit(main())
