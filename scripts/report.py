"""Markdown report for retrieve eval. Does not change baseline_report.md."""
from __future__ import annotations


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def render_last_report(
    *,
    git_hash: str,
    index_id: str,
    started_at: str,
    metrics: dict,
    baseline: dict | None,
    gate_ok: bool,
    gate_reasons: list[str],
    rows: list[dict],
) -> str:
    """Build eval/last_report.md body including HTML comment with metric definitions."""
    b = baseline or {}

    def cell(key: str) -> str:
        if not baseline:
            return "—"
        return _pct(b[key])

    comment = (
        f"<!-- kb hash: {git_hash}  IndexId: {index_id}  time: {started_at}\n"
        "     Recall@5 = not retrieve_miss / effective items with must_hit\n"
        "     module accuracy = C-intent effective items without module_mixup\n"
        "     path hallucination = illegal paths / extracted paths\n"
        "-->"
    )
    lines = [
        comment,
        "# RAG retrieve report",
        "",
        f"- git: {git_hash}",
        f"- index_id: {index_id}",
        f"- started_at: {started_at}",
        f"- retrieve_error: {metrics.get('n_retrieve_error', 0)}",
        f"- gate_ok: {gate_ok}",
    ]
    if gate_reasons:
        lines.append(f"- gate_reasons: {'; '.join(gate_reasons)}")
    lines += [
        "",
        "| metric | current | baseline | gate |",
        "|--------|---------|----------|------|",
        f"| Recall@5 | {_pct(metrics['recall'])} | {cell('recall')} | drop vs baseline ≤ 5pp and absolute ≥ 80% |",
        f"| 模块准确率 | {_pct(metrics['module_acc'])} | {cell('module_acc')} | not below baseline and absolute ≥ 90% |",
        f"| 幻觉路径率 | {_pct(metrics['halluc_rate'])} | {cell('halluc_rate')} | not above baseline and absolute ≤ 5% |",
        "",
        "## items",
        "",
        "| id | intent | primary | tags | must_hit | paths |",
        "|----|--------|---------|------|----------|-------|",
    ]
    for r in rows:
        tags = ",".join(r.get("tags") or [])
        mh = "pass" if r.get("must_hit_ok") else "fail"
        paths = " ".join(r.get("extracted_paths") or [])
        lines.append(
            f"| {r.get('id')} | {r.get('intent')} | {r.get('primary')} | {tags} | {mh} | {paths} |"
        )
    return "\n".join(lines) + "\n"
