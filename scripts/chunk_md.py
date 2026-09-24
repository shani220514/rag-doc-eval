"""按 ATX 标题把 Markdown 切成可入库的段。不读 .env，不联网。

入库单元是「某一节」，不是整份文件。问分页时，检索应该能单独召回
「列表接口」，而不是把确认接口一起粘进来。

chunk_id 形如 ``cards/purchase-order.md#列表接口``。sha256 是该段正文的
UTF-8 摘要（读入后换行已规范成 ``\\n``），同一节没改则摘要不变。
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

# 行首的 # 标题。不切正文里的行内井号。
_HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$", re.MULTILINE)


def chunk_sha256(content: str) -> str:
    """这一段正文的 sha256。改字才变，用来做增量入库的比对键。"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _unique_title(title: str, seen: dict[str, int]) -> str:
    """同文件里标题重复时，第二条起加 ``-2``、``-3``，避免 chunk_id 撞车。"""
    seen[title] = seen.get(title, 0) + 1
    if seen[title] == 1:
        return title
    return f"{title}-{seen[title]}"


def _pack(rel_posix: str, title: str, content: str) -> dict:
    content = content.strip("\n")
    return {
        "file_name": rel_posix,
        "title": title,
        "chunk_id": f"{rel_posix}#{title}",
        "content": content,
        "sha256": chunk_sha256(content),
    }


def split_markdown(rel_posix: str, text: str) -> list[dict]:
    """把一份 Markdown 切成有序切片。

    每个 ATX 标题（``#`` 到 ``######``）单独成段，正文一直到下一个标题。
    文首 YAML 前言没有标题，挂到第一节上，这样别名还在「导读」里，
    又不会多出一段只有元数据的切片。没有标题的文件整篇作为一段，
    标题用文件名（不含扩展名）。
    """
    matches = list(_HEADING.finditer(text))
    if not matches:
        title = Path(rel_posix).stem
        return [_pack(rel_posix, title, text)]

    seen: dict[str, int] = {}
    chunks: list[dict] = []
    for index, match in enumerate(matches):
        # 第一节从文件开头算起，从而带上前面的前言。
        start = 0 if index == 0 else match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        title = _unique_title(match.group(2).strip(), seen)
        chunks.append(_pack(rel_posix, title, text[start:end]))
    return chunks
