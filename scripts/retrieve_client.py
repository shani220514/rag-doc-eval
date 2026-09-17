"""Retrieve client with throttling retries.

HTTP I/O is injected (`post_json`, `sleep`) so tests never open sockets.
The JSON shape is DashScope-compatible (`output.nodes`).
"""
from __future__ import annotations

from typing import Callable, Mapping, Sequence

Chunk = dict

DEFAULT_RETRIEVE_URL = "https://dashscope.aliyuncs.com/api/v1/indices/retrieve"

_RETRY_BACKOFFS: tuple[int, ...] = (2, 4, 8)


class RetrieveError(RuntimeError):
    """Raised when retrieve exhausts retries or returns a non-OK response."""


def parse_retrieve_body(payload: Mapping) -> list[Chunk]:
    """Map a DashScope-like retrieve response body to a list of chunks."""
    output = payload.get("output") if isinstance(payload, Mapping) else None
    if isinstance(output, Mapping):
        nodes = output.get("nodes")
    else:
        nodes = None
    if nodes is None:
        nodes = payload.get("nodes") if isinstance(payload, Mapping) else None
    if not isinstance(nodes, Sequence):
        return []

    chunks: list[Chunk] = []
    for node in nodes:
        if not isinstance(node, Mapping):
            continue
        text = node.get("text")
        if text is None:
            text = node.get("content")
        if text is None:
            text = ""
        meta = node.get("metadata") if isinstance(node.get("metadata"), Mapping) else {}
        file_name = (
            meta.get("file_name")
            or meta.get("doc_name")
            or meta.get("title")
            or ""
        )
        chunks.append(
            {
                "content": text,
                "file_name": file_name,
                "title": meta.get("title", ""),
                "doc_name": meta.get("doc_name", ""),
            }
        )
    return chunks


def _looks_throttled(status: int, body: Mapping) -> bool:
    if status == 429:
        return True
    if status in (200, 201):
        return False
    if isinstance(body, Mapping):
        msg = str(body.get("message", "")).lower()
        code = str(body.get("code", "")).lower()
        return "throttl" in msg or "rate" in msg or "429" in code or "throttl" in code
    return False


def _is_success_body(body: Mapping) -> bool:
    if not isinstance(body, Mapping):
        return True
    code = body.get("code")
    if code is None or code == "":
        return True
    return str(code).lower() in ("0", "success", "ok")


def retrieve_top5(
    query: str,
    *,
    post_json: Callable[[str, Mapping, Mapping], tuple[int, Mapping]],
    sleep: Callable[[float], None],
    url: str = DEFAULT_RETRIEVE_URL,
    api_key: str = "",
    workspace_id: str = "",
    pipeline_id: str = "",
    body: Mapping | None = None,
) -> list[Chunk]:
    """Retrieve top-5 dense chunks for ``query`` with throttling retries."""
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if workspace_id:
        headers["X-DashScope-WorkSpace"] = workspace_id

    if body is None:
        body = {
            "input": {"query": query},
            "parameters": {
                "dense_similarity_top_k": 5,
            },
        }
        if pipeline_id:
            body["parameters"]["pipeline_id"] = pipeline_id  # type: ignore[index]

    last_status: int = 0
    last_body: Mapping = {}
    for attempt, backoff in enumerate([0, *_RETRY_BACKOFFS]):
        if attempt > 0:
            sleep(backoff)
        status, resp = post_json(url, body, headers)
        last_status, last_body = status, resp if isinstance(resp, Mapping) else {}
        if status in (200, 201) and _is_success_body(last_body):
            return parse_retrieve_body(last_body)
        if _looks_throttled(status, last_body) and attempt < len(_RETRY_BACKOFFS):
            continue
        break

    raise RetrieveError(
        f"retrieve failed after {len(_RETRY_BACKOFFS)} retries: "
        f"status={last_status} body={last_body!r}"
    )
