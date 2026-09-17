from report import render_last_report


def test_report_contains_hash_and_tables():
    metrics = {"recall": 0.825, "module_acc": 1.0, "halluc_rate": 0.0, "n_retrieve_error": 0}
    rows = [{
        "id": "A-01",
        "intent": "A_penetrate",
        "primary": "ok",
        "tags": [],
        "must_hit_ok": True,
        "extracted_paths": ["/v1/purchase-orders"],
    }]
    md = render_last_report(
        git_hash="abcdef1",
        index_id="idx",
        started_at="2026-09-17T00:00:00+08:00",
        metrics=metrics,
        baseline=None,
        gate_ok=True,
        gate_reasons=[],
        rows=rows,
    )
    assert "abcdef1" in md
    assert "Recall@5" in md
    assert "A-01" in md
    assert "kb hash" in md
