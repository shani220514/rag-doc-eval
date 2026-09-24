<!-- kb hash: e0d9e20  IndexId:   time: 2026-09-24T16:27:31.064435+08:00
     Recall@5 = not retrieve_miss / effective items with must_hit（未出现 retrieve_miss 的题 / 带 must_hit 的有效题）
     module accuracy = C-intent effective items without module_mixup（C 类有效题中未出现 module_mixup 的比例）
     path hallucination = illegal paths / extracted paths（非法路径条数 / 抽出路径条数）
-->
# RAG retrieve report

- git: e0d9e20
- index_id: 
- started_at: 2026-09-24T16:27:31.064435+08:00
- retrieve_error: 0
- gate_ok: True

| metric | current | baseline | gate |
|--------|---------|----------|------|
| Recall@5 | 100.0% | — | drop vs baseline ≤ 5pp and absolute ≥ 80% |
| 模块准确率 | 100.0% | — | not below baseline and absolute ≥ 90% |
| 幻觉路径率 | 0.0% | — | not above baseline and absolute ≤ 5% |

## items

| id | intent | primary | tags | must_hit | paths |
|----|--------|---------|------|----------|-------|
| A-01 | A_penetrate | ok |  | pass | /v1/purchase-orders |
| A-02 | A_penetrate | ok |  | pass |  |
| A-03 | A_penetrate | ok |  | pass |  |
| A-04 | A_penetrate | ok |  | pass | /v1/purchase-orders |
| A-05 | A_penetrate | ok |  | pass | /v1/purchase-orders |
| A-06 | A_penetrate | ok |  | pass | /v1/purchase-orders/{orderId} |
| A-07 | A_penetrate | ok |  | pass | /v1/purchase-orders/{orderId} |
| A-08 | A_penetrate | ok |  | pass | /v1/purchase-orders/status |
| A-09 | A_penetrate | ok |  | pass | /v1/purchase-orders/status |
| A-10 | A_penetrate | ok |  | pass | /v1/purchase-orders/{orderId}/ack |
| A-11 | A_penetrate | ok |  | pass | /v1/purchase-orders/{orderId}/ack |
| A-12 | A_penetrate | ok |  | pass | /v1/purchase-orders |
| A-13 | A_penetrate | ok |  | pass | /v1/purchase-orders/{orderId} |
| A-14 | A_penetrate | ok |  | pass | /v1/purchase-orders |
| A-15 | A_penetrate | ok |  | pass | /v1/purchase-orders |
| A-16 | A_penetrate | ok |  | pass |  |
| B-01 | B_source | ok |  | pass | /v1/purchase-orders |
| B-02 | B_source | ok |  | pass | /v1/purchase-orders |
| B-03 | B_source | ok |  | pass | /v1/purchase-orders/{orderId} |
| B-04 | B_source | ok |  | pass | /v1/purchase-orders/{orderId} |
| B-05 | B_source | ok |  | pass | /v1/purchase-orders/status |
| B-06 | B_source | ok |  | pass | /v1/purchase-orders/{orderId}/ack |
| B-07 | B_source | ok |  | pass | /v1/purchase-orders |
| B-08 | B_source | ok |  | pass | /v1/purchase-orders/status |
| C-01 | C_module_trap | ok |  | pass |  |
| C-02 | C_module_trap | ok |  | pass |  |
| C-03 | C_module_trap | ok |  | pass |  |
| C-04 | C_module_trap | ok |  | pass |  |
| C-05 | C_module_trap | ok |  | pass |  |
| C-06 | C_module_trap | ok |  | pass |  |
| C-07 | C_module_trap | ok |  | pass |  |
| C-08 | C_module_trap | ok |  | pass |  |
| D-01 | D_constraint | ok |  | pass | /v1/purchase-orders/{orderId} |
| D-02 | D_constraint | ok |  | pass | /v1/purchase-orders/status |
| D-03 | D_constraint | ok |  | pass | /v1/purchase-orders |
| D-04 | D_constraint | ok |  | pass | /v1/purchase-orders |
| E-01 | E_path_faithful | ok |  | pass | /v1/purchase-orders |
| E-02 | E_path_faithful | ok |  | pass | /v1/purchase-orders/{orderId} |
| E-03 | E_path_faithful | ok |  | pass | /v1/purchase-orders/status |
| E-04 | E_path_faithful | ok |  | pass | /v1/purchase-orders/{orderId}/ack |
