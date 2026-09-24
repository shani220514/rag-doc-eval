"""正式夹具必须是真实标题切片，而且每题的 must_hit 都落在所选的那一段里。"""
from __future__ import annotations

import json

import yaml

from chunk_md import split_markdown
from kb_paths import repo_root
from path_extract import extract_paths


def _corpus_chunks() -> dict[str, dict]:
    root = repo_root()
    found: dict[str, dict] = {}
    for sub in ("cards", "sources"):
        base = root / sub
        for path in sorted(base.rglob("*.md")):
            rel = path.relative_to(root).as_posix()
            text = path.read_text(encoding="utf-8")
            for chunk in split_markdown(rel, text):
                found[chunk["chunk_id"]] = chunk
    return found


def test_fixture_chunks_match_heading_splits_and_cover_needles():
    root = repo_root()
    picks = yaml.safe_load(
        (root / "tests" / "fixtures" / "chunk_pick.yaml").read_text(encoding="utf-8")
    )["picks"]
    goldens = yaml.safe_load(
        (root / "eval" / "goldens.yaml").read_text(encoding="utf-8")
    )["goldens"]
    fixture = json.loads(
        (root / "tests" / "fixtures" / "fake_retrieve.json").read_text(encoding="utf-8")
    )
    catalog = _corpus_chunks()

    assert set(picks) == {g["id"] for g in goldens}
    for golden in goldens:
        gid = golden["id"]
        chunks = fixture[gid]
        assert 1 <= len(chunks) <= 5, gid
        picked = catalog[picks[gid]]
        assert chunks[0]["chunk_id"] == picks[gid]
        assert chunks[0]["content"] == picked["content"]
        assert chunks[0]["file_name"] == picked["file_name"]
        assert chunks[0]["title"] == picked["title"]
        blob = chunks[0]["content"]
        for needle in golden["must_hit"]:
            assert needle in blob, f"{gid} missing {needle!r}"
        forbidden = set(golden.get("forbidden_top1_basenames") or [])
        top1 = chunks[0]["file_name"].rsplit("/", 1)[-1]
        assert top1 not in forbidden, gid

    # 列表题只抽出列表路径，不再把详情/状态/确认路径一起带进来。
    listed = extract_paths(fixture["A-01"][0]["content"])
    assert listed == ["/v1/purchase-orders"]
    intro = fixture["A-02"][0]["content"]
    assert "/v1/purchase-orders/{orderId}/ack" not in intro
