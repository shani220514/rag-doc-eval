from eval_scoring import aggregate_metrics, concat_top5, count_illegal_paths, gate_metrics, score_item

C_FORBIDDEN = [
    "list-orders.md",
    "get-order.md",
    "order-status.md",
    "acknowledge.md",
]


def _g(**kwargs):
    """拼一道黄金题，缺省字段用空列表，测试里只覆盖要改的项。"""
    base = {
        "id": "X",
        "intent": "A_penetrate",
        "question": "q",
        "must_hit": [],
        "must_not_hit": [],
        "forbidden_top1_basenames": [],
        "forbidden_paths": [],
    }
    base.update(kwargs)
    return base


def test_concat_uses_basename_title_content():
    """Top5 拼接必须带上文件名、标题、正文，打分只看这段拼出来的字。"""
    text = concat_top5([
        {"file_name": "cards/purchase-order.md", "title": "T", "content": "hello"},
    ])
    assert "purchase-order.md" in text
    assert "T" in text
    assert "hello" in text


def test_retrieve_error_skips_rest():
    """取切片失败时直接记 retrieve_error，后面的针、模块、路径都不再判。"""
    r = score_item(_g(must_hit=["x"]), [], [], retrieve_error=True)
    assert r["primary"] == "retrieve_error"
    assert r["tags"] == ["retrieve_error"]


def test_retrieve_miss_when_needle_absent():
    """must_hit 有一根针没出现在 Top5 里，主分类就是 retrieve_miss。"""
    chunks = [{"file_name": "cards/purchase-order.md", "title": "", "content": "list"}]
    r = score_item(_g(id="A-01", must_hit=["NOPE"]), chunks, [])
    assert r["primary"] == "retrieve_miss"
    assert "retrieve_miss" in r["tags"]


def test_ok_when_all_needles_present():
    """全部针都在 Top5 里，抽出的路径也在白名单，这题才是 ok。"""
    chunks = [{
        "file_name": "cards/purchase-order.md",
        "title": "",
        "content": "list /v1/purchase-orders",
    }]
    r = score_item(
        _g(id="A-01", must_hit=["/v1/purchase-orders", "list"]),
        chunks,
        ["/v1/purchase-orders"],
    )
    assert r["primary"] == "ok"


def test_c_mixup_on_forbidden_top1():
    """C 类针命中了，但 Top1 仍是禁止的采购文档，主分类为 module_mixup。"""
    chunks = [{
        "file_name": "sources/api/list-orders.md",
        "title": "",
        "content": "发运与销售订单不是本卡",
    }]
    r = score_item(
        _g(
            id="C-01",
            intent="C_module_trap",
            must_hit=["发运与销售订单不是本卡"],
            forbidden_top1_basenames=C_FORBIDDEN,
        ),
        chunks,
        [],
    )
    assert r["primary"] == "module_mixup"
    assert "module_mixup" in r["tags"]


def test_c_miss_still_tags_mixup():
    """C 类针也没命中时，主分类仍是 miss；mixup 只记 tag，不抢主分类。"""
    chunks = [{
        "file_name": "sources/api/list-orders.md",
        "title": "",
        "content": "purchase-orders only",
    }]
    r = score_item(
        _g(
            id="C-01",
            intent="C_module_trap",
            must_hit=["发运与销售订单不是本卡"],
            forbidden_top1_basenames=C_FORBIDDEN,
        ),
        chunks,
        [],
    )
    assert r["primary"] == "retrieve_miss"
    assert "module_mixup" in r["tags"]


def test_must_not_hit_maps_to_retrieve_miss_primary():
    """踩到 must_not_hit 也算召回失败，主分类映射成 retrieve_miss。"""
    chunks = [{"file_name": "x.md", "title": "", "content": "leak secret-token"}]
    r = score_item(_g(must_hit=["leak"], must_not_hit=["secret-token"]), chunks, [])
    assert r["primary"] == "retrieve_miss"


def test_path_hallucination_unknown_path():
    """针命中了，但抽出的路径不在白名单，记 path_hallucination。"""
    chunks = [{"file_name": "c.md", "title": "", "content": "ok /v1/unknown/path list"}]
    r = score_item(
        _g(must_hit=["list"], forbidden_paths=[]),
        chunks,
        ["/v1/purchase-orders"],
    )
    assert r["primary"] == "path_hallucination"


def test_forbidden_paths_count_even_if_whitelisted():
    """路径即使在白名单，只要落在该题 forbidden_paths，仍算幻觉。"""
    chunks = [{"file_name": "c.md", "title": "", "content": "/v1/purchase-orders/{orderId}/ack hit"}]
    r = score_item(
        _g(must_hit=["hit"], forbidden_paths=["/v1/purchase-orders/{orderId}/ack"]),
        chunks,
        ["/v1/purchase-orders/{orderId}/ack"],
    )
    assert r["primary"] == "path_hallucination"


def test_score_item_reports_had_must_hit():
    """had_must_hit 只看题目有没有针，跟是否命中、是否 retrieve_error 无关。"""
    chunks = [{"file_name": "c.md", "title": "", "content": "list"}]
    with_needle = score_item(_g(id="A-01", must_hit=["list"]), chunks, [])
    assert with_needle["had_must_hit"] is True
    without_needle = score_item(_g(id="A-02", must_hit=[]), chunks, [])
    assert without_needle["had_must_hit"] is False
    errored = score_item(_g(id="A-03", must_hit=["list"]), chunks, [], retrieve_error=True)
    assert errored["had_must_hit"] is True


def test_aggregate_recall_and_halluc():
    """汇总时 error 题不算有效题；Recall@5 只在带针的有效题上平均。"""
    rows = [
        {"intent": "A_penetrate", "primary": "ok", "tags": [], "must_hit_ok": True, "extracted_paths": ["/v1/a"], "had_must_hit": True},
        {"intent": "A_penetrate", "primary": "retrieve_miss", "tags": ["retrieve_miss"], "must_hit_ok": False, "extracted_paths": [], "had_must_hit": True},
        {"intent": "C_module_trap", "primary": "ok", "tags": [], "must_hit_ok": True, "extracted_paths": [], "had_must_hit": True},
        {"intent": "A_penetrate", "primary": "retrieve_error", "tags": ["retrieve_error"], "must_hit_ok": False, "extracted_paths": []},
    ]
    m = aggregate_metrics(rows, illegal_path_count=1, extracted_path_count=2)
    assert m["n_retrieve_error"] == 1
    assert abs(m["recall"] - 2 / 3) < 1e-9
    assert m["module_acc"] == 1.0
    assert abs(m["halluc_rate"] - 0.5) < 1e-9
    assert m["n_effective"] == 3
    assert m["n_must_hit"] == 3
    assert m["n_c"] == 1
    assert m["n_illegal_paths"] == 1
    assert m["n_extracted_paths"] == 2


def test_aggregate_vacuous_denominators():
    """空题集时汇总比率用约定空分母（recall/module=1，幻觉=0），门禁另挂。"""
    m = aggregate_metrics([], illegal_path_count=0, extracted_path_count=0)
    assert m["recall"] == 1.0
    assert m["module_acc"] == 1.0
    assert m["halluc_rate"] == 0.0
    assert m["n_effective"] == 0
    assert m["n_must_hit"] == 0
    assert m["n_c"] == 0


def test_module_acc_counts_tag_not_only_primary():
    """模块准确率看 tags 里有没有 mixup，即使主分类已被 miss 抢占也要扣。"""
    rows = [
        {
            "intent": "C_module_trap",
            "primary": "retrieve_miss",
            "tags": ["retrieve_miss", "module_mixup"],
            "must_hit_ok": False,
            "extracted_paths": [],
            "had_must_hit": True,
        }
    ]
    m = aggregate_metrics(rows, 0, 0)
    assert m["module_acc"] == 0.0


def test_gate_absolute_and_relative():
    """绝对门槛 Recall@5≥80%；有 baseline 时，相对再掉超过 5 个百分点也挂。"""
    cur = {"recall": 0.82, "module_acc": 1.0, "halluc_rate": 0.0, "n_effective": 40}
    ok, reasons = gate_metrics(cur, None)
    assert ok and reasons == []
    bad = {"recall": 0.70, "module_acc": 1.0, "halluc_rate": 0.0, "n_effective": 40}
    ok, reasons = gate_metrics(bad, None)
    assert not ok
    base = {"recall": 0.90, "module_acc": 1.0, "halluc_rate": 0.0}
    drop = {"recall": 0.84, "module_acc": 1.0, "halluc_rate": 0.0, "n_effective": 40}
    ok, reasons = gate_metrics(drop, base)
    assert not ok


def test_count_illegal_paths_walks_extracted():
    """幻觉率分母是抽出的路径条数；error 题跳过，forbidden 即使抽出也算非法。"""
    rows = [
        {"id": "A-01", "primary": "ok", "extracted_paths": ["/v1/a", "/v1/b"]},
        {"id": "A-02", "primary": "retrieve_error", "extracted_paths": ["/v1/c"]},
    ]
    goldens_by_id = {"A-01": {"forbidden_paths": ["/v1/b"]}}
    illegal, extracted = count_illegal_paths(rows, ["/v1/a"], goldens_by_id)
    assert illegal == 1
    assert extracted == 2


def test_gate_fails_when_no_effective_questions():
    """全部 retrieve_error 时有效题为 0，门禁必须失败，不能显示 100% 通过。"""
    m = aggregate_metrics(
        [
            {"intent": "A_penetrate", "primary": "retrieve_error",
             "tags": ["retrieve_error"], "extracted_paths": [], "had_must_hit": True},
        ],
        illegal_path_count=0,
        extracted_path_count=0,
    )
    assert m["n_effective"] == 0
    ok, reasons = gate_metrics(m, None)
    assert not ok
    assert any("no effective" in r for r in reasons)


def test_gate_fails_when_empty_rows():
    """一行题都没有同样视为无有效题，门禁失败。"""
    m = aggregate_metrics([], illegal_path_count=0, extracted_path_count=0)
    assert m["n_effective"] == 0
    ok, reasons = gate_metrics(m, None)
    assert not ok
    assert any("no effective" in r for r in reasons)
