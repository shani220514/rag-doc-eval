import pytest
from retrieve_client import RetrieveError, parse_retrieve_body, retrieve_top5


def test_parse_nodes():
    payload = {
        "output": {
            "nodes": [
                {"text": "hello", "metadata": {"doc_name": "cards/purchase-order.md", "title": "导读"}},
            ]
        }
    }
    chunks = parse_retrieve_body(payload)
    assert chunks[0]["content"] == "hello"
    assert chunks[0]["file_name"] == "cards/purchase-order.md"


def test_retry_then_ok():
    calls = {"n": 0}

    def post_json(_url, _body, _headers):
        calls["n"] += 1
        if calls["n"] < 3:
            return 429, {"message": "Throttling"}
        return 200, {"output": {"nodes": [{"text": "x", "metadata": {"doc_name": "a.md"}}]}}

    sleeps = []
    chunks = retrieve_top5("q", post_json=post_json, sleep=lambda s: sleeps.append(s))
    assert calls["n"] == 3
    assert sleeps == [2, 4]
    assert chunks[0]["content"] == "x"


def test_retry_exhausted():
    def post_json(_u, _b, _h):
        return 429, {}

    with pytest.raises(RetrieveError):
        retrieve_top5("q", post_json=post_json, sleep=lambda _s: None)


def test_non_success_json_code_raises():
    def post_json(_u, _b, _h):
        return 200, {"code": "InvalidApiKey", "message": "bad key"}

    with pytest.raises(RetrieveError, match="InvalidApiKey"):
        retrieve_top5("q", post_json=post_json, sleep=lambda _s: None)


def test_success_code_zero_returns_chunks():
    def post_json(_u, _b, _h):
        return 200, {"code": "0", "output": {"nodes": [{"text": "ok", "metadata": {"doc_name": "a.md"}}]}}

    chunks = retrieve_top5("q", post_json=post_json, sleep=lambda _s: None)
    assert chunks and chunks[0]["content"] == "ok"
