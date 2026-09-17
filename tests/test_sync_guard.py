import pytest
from sync_guard import SyncGuardError, assert_uploadable, find_secret_hits, is_sync_allowed


def test_allows_cards_and_sources_md():
    assert is_sync_allowed("cards/purchase-order.md") is True
    assert is_sync_allowed("sources/api/list-orders.md") is True


def test_rejects_eval_and_env():
    assert is_sync_allowed("eval/goldens.yaml") is False
    assert is_sync_allowed(".env") is False
    assert is_sync_allowed("cards/po.json") is False


def test_secret_patterns():
    assert "Bearer " in find_secret_hits("Authorization: Bearer abc")
    assert "password" in find_secret_hits("password=123")
    assert "AKIA" in find_secret_hits("AKIAIOSFODNN7EXAMPLE")
    assert find_secret_hits("普通说明 code=10000") == []


def test_assert_uploadable_raises():
    with pytest.raises(SyncGuardError, match="not in sync allowlist"):
        assert_uploadable("README.md", "hi")
    with pytest.raises(SyncGuardError, match="secret"):
        assert_uploadable("cards/purchase-order.md", "Bearer tok")
    assert_uploadable("cards/purchase-order.md", "采购订单列表")
