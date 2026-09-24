<!-- kb hash: c610876  IndexId:   time: 2026-09-24T15:13:36.970991+08:00
     Recall@5 = not retrieve_miss / effective items with must_hit（未出现 retrieve_miss 的题 / 带 must_hit 的有效题）
     module accuracy = C-intent effective items without module_mixup（C 类有效题中未出现 module_mixup 的比例）
     path hallucination = illegal paths / extracted paths（非法路径条数 / 抽出路径条数）
-->
# RAG retrieve report

- git: c610876
- index_id: 
- started_at: 2026-09-24T15:13:36.970991+08:00
- retrieve_error: 0
- gate_ok: False
- gate_reasons: Recall@5 < 80%; module accuracy < 90%; hallucination path rate > 5%

| metric | current | baseline | gate |
|--------|---------|----------|------|
| Recall@5 | 40.0% | — | drop vs baseline ≤ 5pp and absolute ≥ 80% |
| 模块准确率 | 30.0% | — | not below baseline and absolute ≥ 90% |
| 幻觉路径率 | 20.0% | — | not above baseline and absolute ≤ 5% |

## items

| id | intent | primary | tags | must_hit | paths |
|----|--------|---------|------|----------|-------|
| A-01 | A_penetrate | ok |  | pass | /v1/purchase-orders |
| A-02 | A_penetrate | ok |  | pass | /v1/purchase-orders |
| A-03 | A_penetrate | path_hallucination | path_hallucination | pass | /v1/shipments |
| A-04 | A_penetrate | retrieve_miss | retrieve_miss | fail | /v1/purchase-orders |
| A-05 | A_penetrate | retrieve_miss | retrieve_miss,path_hallucination | fail | /v1/shipments |
| C-01 | C_module_trap | ok |  | pass | /v1/purchase-orders |
| C-02 | C_module_trap | ok |  | pass | /v1/purchase-orders |
| C-03 | C_module_trap | ok |  | pass | /v1/purchase-orders |
| C-04 | C_module_trap | retrieve_miss | retrieve_miss,module_mixup | fail | /v1/purchase-orders |
| C-05 | C_module_trap | retrieve_miss | retrieve_miss,module_mixup | fail | /v1/purchase-orders |
| C-06 | C_module_trap | retrieve_miss | retrieve_miss,module_mixup | fail | /v1/purchase-orders |
| C-07 | C_module_trap | retrieve_miss | retrieve_miss,module_mixup | fail | /v1/purchase-orders |
| C-08 | C_module_trap | retrieve_miss | retrieve_miss,module_mixup | fail | /v1/purchase-orders |
| C-09 | C_module_trap | retrieve_miss | retrieve_miss,module_mixup | fail | /v1/purchase-orders |
| C-10 | C_module_trap | retrieve_miss | retrieve_miss,module_mixup,path_hallucination | fail | /v1/shipments |
