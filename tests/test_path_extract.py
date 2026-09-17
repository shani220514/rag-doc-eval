from path_extract import extract_paths, whitelist_yaml


def test_extract_backtick_and_bare_and_strip_punct():
    text = (
        "见 `/v1/purchase-orders` 与 "
        "/v1/purchase-orders/{orderId}。还有 GET /v1/purchase-orders/status"
    )
    paths = extract_paths(text)
    assert "/v1/purchase-orders" in paths
    assert "/v1/purchase-orders/{orderId}" in paths
    assert "/v1/purchase-orders/status" in paths
    assert all(not p.startswith("GET") for p in paths)


def test_dedupe_preserves_order():
    text = "/v1/a /v1/b /v1/a"
    assert extract_paths(text) == ["/v1/a", "/v1/b"]


def test_whitelist_yaml_header():
    body = whitelist_yaml(["/v1/a"])
    assert "Do not hand-edit" in body
    assert "- /v1/a" in body
