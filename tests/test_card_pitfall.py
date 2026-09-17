from kb_paths import repo_root


def test_card_has_required_pitfall_and_layers():
    text = (repo_root() / "cards" / "purchase-order.md").read_text(encoding="utf-8")
    assert "发运与销售订单不是本卡" in text
    for h in [
        "## 导读",
        "## 列表接口",
        "## 详情接口",
        "## 状态接口",
        "## 确认接口",
        "## 已知坑",
        "## 相关链接",
    ]:
        assert h in text
    assert "Bearer " not in text
