"""Heading chunks for cards/ and sources/. No network."""
from __future__ import annotations

from kb_paths import repo_root
from chunk_md import split_markdown


def test_purchase_order_splits_on_atx_headings():
    text = (repo_root() / "cards" / "purchase-order.md").read_text(encoding="utf-8")
    chunks = split_markdown("cards/purchase-order.md", text)
    titles = [c["title"] for c in chunks]
    assert titles == ["导读", "列表接口", "详情接口", "状态接口", "确认接口", "已知坑", "相关链接"]
    by_title = {c["title"]: c for c in chunks}
    listed = by_title["列表接口"]
    assert listed["file_name"] == "cards/purchase-order.md"
    assert listed["chunk_id"] == "cards/purchase-order.md#列表接口"
    assert "page_size" in listed["content"]
    assert "确认接口" not in listed["content"]
    assert len(listed["sha256"]) == 64
    # 文首 YAML 跟第一节走，避免单独成一段没有正文的切片。
    assert "id: purchase-order" in by_title["导读"]["content"]
    assert "id: purchase-order" not in listed["content"]


def test_source_spec_is_one_chunk():
    text = (repo_root() / "sources" / "api" / "list-orders.md").read_text(encoding="utf-8")
    chunks = split_markdown("sources/api/list-orders.md", text)
    assert len(chunks) == 1
    assert chunks[0]["title"] == "List purchase orders"
    assert chunks[0]["chunk_id"] == "sources/api/list-orders.md#List purchase orders"
    assert "default 50" in chunks[0]["content"]


def test_headingless_body_is_one_chunk():
    chunks = split_markdown("cards/note.md", "plain body\n")
    assert len(chunks) == 1
    assert chunks[0]["title"] == "note"
    assert chunks[0]["chunk_id"] == "cards/note.md#note"
    assert chunks[0]["content"] == "plain body"


def test_duplicate_heading_gets_numeric_suffix():
    text = "## 同名\n\na\n\n## 同名\n\nb\n"
    chunks = split_markdown("cards/a.md", text)
    assert [c["chunk_id"] for c in chunks] == [
        "cards/a.md#同名",
        "cards/a.md#同名-2",
    ]
    assert chunks[1]["content"].endswith("b")
