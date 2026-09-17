from collections import Counter

import yaml
from kb_paths import repo_root

ALLOWED = {
    "A_penetrate",
    "B_source",
    "C_module_trap",
    "D_constraint",
    "E_path_faithful",
}
C_FILES = {
    "list-orders.md",
    "get-order.md",
    "order-status.md",
    "acknowledge.md",
}
REQUIRED_IDS = {"A-01", "B-01", "C-01", "D-01", "E-01"}


def _load_goldens():
    data = yaml.safe_load((repo_root() / "eval" / "goldens.yaml").read_text(encoding="utf-8"))
    return data["goldens"] if isinstance(data, dict) else data


def _corpus_text():
    root = repo_root()
    files = sorted((root / "cards").rglob("*.md"))
    files += sorted((root / "sources").rglob("*.md"))
    return "\n".join(p.read_text(encoding="utf-8") for p in files)


def test_goldens_schema_and_quota():
    items = _load_goldens()
    assert isinstance(items, list)
    ids = [x["id"] for x in items]
    assert len(ids) == len(set(ids)) >= 40
    assert REQUIRED_IDS <= set(ids)
    counts = Counter(x["intent"] for x in items)
    assert counts["A_penetrate"] == 16
    assert counts["B_source"] == 8
    assert counts["C_module_trap"] == 8
    assert counts["D_constraint"] == 4
    assert counts["E_path_faithful"] == 4
    for x in items:
        assert x["intent"] in ALLOWED
        assert isinstance(x["must_hit"], list) and x["must_hit"]
        if x["intent"] == "C_module_trap":
            assert set(x.get("forbidden_top1_basenames") or []) == C_FILES
    a01 = next(x for x in items if x["id"] == "A-01")
    assert "/v1/purchase-orders" in a01["must_hit"]


def test_goldens_needles_in_corpus():
    items = _load_goldens()
    corpus = _corpus_text()
    missing: list[tuple[str, str]] = []
    for x in items:
        for needle in x["must_hit"]:
            if needle not in corpus:
                missing.append((x["id"], needle))
    assert not missing, f"must_hit needles not found in cards+sources corpus: {missing}"
