"""Rule scorer for Retrieve Top5. No LLM, no network.

Why retrieve_miss outranks mixup: a miss means the disambiguation needle
never appeared; mixup is still recorded in tags for module accuracy.
"""
from __future__ import annotations

from pathlib import Path

from path_extract import extract_paths


def basename_of(file_name: str) -> str:
    """POSIX or Windows path -> file name only."""
    if not file_name:
        return ""
    return Path(str(file_name).replace("\\", "/")).name


def concat_top5(chunks: list[dict]) -> str:
    """Join Top5 as basename + title + content. Missing keys become empty."""
    parts: list[str] = []
    for ch in chunks:
        base = basename_of(str(ch.get("file_name") or ""))
        title = str(ch.get("title") or "")
        content = str(ch.get("content") or "")
        parts.append(f"{base}\n{title}\n{content}")
    return "\n---\n".join(parts)


def score_item(
    golden: dict,
    chunks: list[dict],
    whitelist: list[str],
    retrieve_error: bool = False,
) -> dict:
    """Return primary label and tags."""
    gid = str(golden.get("id") or "")
    intent = str(golden.get("intent") or "")
    must_hit = list(golden.get("must_hit") or [])
    must_not_hit = list(golden.get("must_not_hit") or [])
    forbidden_top1 = list(golden.get("forbidden_top1_basenames") or [])
    forbidden_paths = list(golden.get("forbidden_paths") or [])
    tags: list[str] = []

    if retrieve_error:
        return {
            "id": gid,
            "intent": intent,
            "primary": "retrieve_error",
            "tags": ["retrieve_error"],
            "must_hit_ok": False,
            "had_must_hit": bool(must_hit),
            "extracted_paths": [],
            "top1_basename": "",
        }

    blob = concat_top5(chunks)
    top1 = basename_of(str((chunks[0] if chunks else {}).get("file_name") or ""))
    extracted = extract_paths(blob)

    miss = bool(must_hit) and any(needle not in blob for needle in must_hit)
    if miss:
        tags.append("retrieve_miss")

    if any(n and n in blob for n in must_not_hit):
        tags.append("must_not_hit_fail")

    mixup = intent == "C_module_trap" and top1 in set(forbidden_top1)
    if mixup:
        tags.append("module_mixup")

    allow = set(whitelist)
    forbidden_set = set(forbidden_paths)
    if any(p not in allow for p in extracted) or any(p in forbidden_set for p in extracted):
        tags.append("path_hallucination")

    if "retrieve_error" in tags:
        primary = "retrieve_error"
    elif "retrieve_miss" in tags:
        primary = "retrieve_miss"
    elif "module_mixup" in tags:
        primary = "module_mixup"
    elif "must_not_hit_fail" in tags:
        primary = "retrieve_miss"
        if "retrieve_miss" not in tags:
            tags.append("retrieve_miss")
    elif "path_hallucination" in tags:
        primary = "path_hallucination"
    else:
        primary = "ok"

    return {
        "id": gid,
        "intent": intent,
        "primary": primary,
        "tags": tags,
        "must_hit_ok": not miss,
        "had_must_hit": bool(must_hit),
        "extracted_paths": extracted,
        "top1_basename": top1,
    }


def aggregate_metrics(
    rows: list[dict],
    illegal_path_count: int,
    extracted_path_count: int,
) -> dict:
    """Compute Recall@5, module accuracy, path hallucination rate."""
    effective = [r for r in rows if r.get("primary") != "retrieve_error"]
    errors = len(rows) - len(effective)
    hit_pool = [r for r in effective if r.get("had_must_hit")]
    recall_num = sum(1 for r in hit_pool if "retrieve_miss" not in r.get("tags", []))
    recall = 1.0 if not hit_pool else recall_num / len(hit_pool)
    c_pool = [r for r in effective if r.get("intent") == "C_module_trap"]
    mix = sum(1 for r in c_pool if "module_mixup" in r.get("tags", []))
    module_acc = 1.0 if not c_pool else (len(c_pool) - mix) / len(c_pool)
    halluc = 0.0 if extracted_path_count == 0 else illegal_path_count / extracted_path_count
    return {
        "recall": recall,
        "module_acc": module_acc,
        "halluc_rate": halluc,
        "n_effective": len(effective),
        "n_retrieve_error": errors,
        "n_must_hit": len(hit_pool),
        "n_c": len(c_pool),
        "n_illegal_paths": illegal_path_count,
        "n_extracted_paths": extracted_path_count,
    }


def gate_metrics(current: dict, baseline: dict | None) -> tuple[bool, list[str]]:
    """Absolute floors plus relative baseline.

    Hard rule: if there are zero effective questions, the gate MUST fail.
    """
    reasons: list[str] = []
    if current.get("n_effective", 0) == 0:
        reasons.append("no effective questions (all retrieve_error or empty)")
        return (False, reasons)
    if current["recall"] < 0.80:
        reasons.append("Recall@5 < 80%")
    if current["module_acc"] < 0.90:
        reasons.append("module accuracy < 90%")
    if current["halluc_rate"] > 0.05:
        reasons.append("hallucination path rate > 5%")
    if baseline is not None:
        if current["recall"] < baseline["recall"] - 0.05:
            reasons.append("Recall@5 dropped more than 5pp vs baseline")
        if current["module_acc"] < baseline["module_acc"]:
            reasons.append("module accuracy dropped vs baseline")
        if current["halluc_rate"] > baseline["halluc_rate"]:
            reasons.append("hallucination path rate rose vs baseline")
    return (not reasons, reasons)


def count_illegal_paths(
    rows: list[dict],
    whitelist: list[str],
    goldens_by_id: dict[str, dict],
) -> tuple[int, int]:
    """Sum extracted paths on effective rows; illegal = not whitelist or in that item forbidden_paths."""
    allow = set(whitelist)
    extracted_n = 0
    illegal_n = 0
    for r in rows:
        if r.get("primary") == "retrieve_error":
            continue
        g = goldens_by_id.get(r.get("id", ""), {})
        forbidden = set(g.get("forbidden_paths") or [])
        for p in r.get("extracted_paths") or []:
            extracted_n += 1
            if p not in allow or p in forbidden:
                illegal_n += 1
    return illegal_n, extracted_n
