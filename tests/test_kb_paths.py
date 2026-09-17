from kb_paths import git_short_hash, repo_root


def test_repo_root_contains_eval_and_scripts():
    root = repo_root()
    assert (root / "scripts").is_dir()
    assert (root / "eval").is_dir()
    assert (root / "cards" / "purchase-order.md").is_file()


def test_git_short_hash_is_hex_or_nogit():
    h = git_short_hash()
    if h == "nogit":
        return
    assert len(h) >= 7
    assert all(c in "0123456789abcdef" for c in h.lower())
