"""CLI: every goldens must_hit must appear in cards/ + sources/."""
import sys
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from kb_paths import repo_root  # noqa: E402


def check_needles() -> list[tuple[str, str]]:
    root = repo_root()
    data = yaml.safe_load((root / "eval" / "goldens.yaml").read_text(encoding="utf-8"))
    items = data["goldens"] if isinstance(data, dict) else data

    corpus_files = sorted((root / "cards").rglob("*.md"))
    corpus_files += sorted((root / "sources").rglob("*.md"))
    corpus = "\n".join(p.read_text(encoding="utf-8") for p in corpus_files)

    missing: list[tuple[str, str]] = []
    for x in items:
        for needle in x["must_hit"]:
            if needle not in corpus:
                missing.append((x["id"], needle))
    return missing


if __name__ == "__main__":
    missing = check_needles()
    if missing:
        print("MISSING NEEDLES:")
        for nid, n in missing:
            print(f"  {nid}: {n!r}")
        raise SystemExit(1)
    print("OK: all must_hit needles found in cards+sources corpus")
