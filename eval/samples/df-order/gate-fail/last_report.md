<!-- kb hash: e0d9e20  IndexId:   time: 2026-09-24T18:15:48.231055+08:00
     Recall@5 = not retrieve_miss / effective items with must_hit（未出现 retrieve_miss 的题 / 带 must_hit 的有效题）
     module accuracy = C-intent effective items without module_mixup（C 类有效题中未出现 module_mixup 的比例）
     path hallucination = illegal paths / extracted paths（非法路径条数 / 抽出路径条数）
-->
# RAG retrieve report

- git: e0d9e20
- index_id: 
- started_at: 2026-09-24T18:15:48.231055+08:00
- retrieve_error: 0
- gate_ok: False
- gate_reasons: Recall@5 < 80%; module accuracy < 90%; hallucination path rate > 5%

| metric | current | baseline | gate |
|--------|---------|----------|------|
| Recall@5 | 58.3% | — | drop vs baseline ≤ 5pp and absolute ≥ 80% |
| 模块准确率 | 25.0% | — | not below baseline and absolute ≥ 90% |
| 幻觉路径率 | 100.0% | — | not above baseline and absolute ≤ 5% |

## items

| id | intent | primary | tags | must_hit | paths |
|----|--------|---------|------|----------|-------|
| DF-01 | A_penetrate | ok |  | pass |  |
| DF-02 | A_penetrate | ok |  | pass |  |
| DF-03 | A_penetrate | ok |  | pass |  |
| DF-04 | D_constraint | retrieve_miss | retrieve_miss,path_hallucination | fail | /v1/shipments |
| DF-05 | D_constraint | ok |  | pass |  |
| DF-06 | A_penetrate | ok |  | pass |  |
| DF-07 | A_penetrate | ok |  | pass |  |
| DF-08 | A_penetrate | retrieve_miss | retrieve_miss,path_hallucination | fail | /v1/shipments |
| DF-09 | C_module_trap | ok |  | pass |  |
| DF-10 | C_module_trap | retrieve_miss | retrieve_miss,module_mixup | fail |  |
| DF-11 | C_module_trap | retrieve_miss | retrieve_miss,module_mixup | fail |  |
| DF-12 | C_module_trap | retrieve_miss | retrieve_miss,module_mixup,path_hallucination | fail | /v1/shipments |
