# rag-doc-eval

Offline-first **RAG retrieve evaluation** harness.

Swap `cards/` + `sources/` for your own docs. The scorer, golden-set schema, path whitelist, secret guard, and CI stay the same. The sample corpus is a **fictional purchase-order API** written for this repo. It is not affiliated with Amazon, Alibaba, or any employer product.

## What you can show in an interview

- 40-question golden set with five intents (penetrate / source / module trap / constraint / path faithful)
- Rule-based Top5 scoring: Recall@5, module accuracy, path hallucination — **no LLM-as-judge**
- Absolute + relative gates (empty or all-error runs fail, they do not pass on 100% defaults)
- `sync_guard` blocks `.env`, eval reports, and secret-shaped text from upload
- Live retrieve is optional; **pytest is fully offline**

## Quick start

```bash
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python scripts/kb_sync.py --dry-run
python scripts/eval_retrieve.py --fixture tests/fixtures/fake_retrieve.json
```

Fixture mode does not read `.env` and does not open the network. `index_id` empty in `eval/last_report.md` means fixture evidence, not a live index run.

## Layout

```
cards/                 # layered knowledge cards (synced)
sources/               # supporting specs (synced)
eval/goldens.yaml      # 40 questions
eval/path_whitelist.yaml   # regenerated from cards+sources, do not hand-edit as truth
scripts/eval_retrieve.py   # fixture / live CLI
scripts/eval_scoring.py    # rule scorer + gates
scripts/sync_guard.py      # upload allowlist + secret patterns
scripts/kb_sync.py         # --dry-run lists sha256; live upsert is a v1 stub
```

## Live retrieve (optional)

Copy `env.example` to `.env`. Live mode needs `RETRIEVE_API_KEY`, `RETRIEVE_WORKSPACE_ID`, `RETRIEVE_INDEX_ID`. The HTTP JSON shape is DashScope-compatible (`output.nodes`). Missing env exits **2** without network.

v1 live document upsert is intentionally unimplemented (`kb_sync.py` without `--dry-run` exits 2 even when keys are present).

## License

MIT. Do not commit `.env`, tokens, or real customer documents.
