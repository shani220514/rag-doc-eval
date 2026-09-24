# RAG generate report

- git: e0d9e20
- started_at: 2026-09-24T18:16:27.015744+08:00
- answer_source: answers
- generate_error: 0
- gate_ok: True

| metric | current | gate |
|--------|---------|------|
| 答案命中率 | 100.0% | ≥ 80% |
| 答案路径幻觉率 | 0.0% | ≤ 5% |

## items

| id | intent | primary | tags | paths |
|----|--------|---------|------|-------|
| A-01 | A_penetrate | ok |  | /v1/purchase-orders |
| A-02 | A_penetrate | ok |  |  |
| A-03 | A_penetrate | ok |  |  |
| A-04 | A_penetrate | ok |  |  |
| A-05 | A_penetrate | ok |  |  |
| A-06 | A_penetrate | ok |  | /v1/purchase-orders/{orderId} |
| A-07 | A_penetrate | ok |  |  |
| A-08 | A_penetrate | ok |  | /v1/purchase-orders/status |
| A-09 | A_penetrate | ok |  |  |
| A-10 | A_penetrate | ok |  | /v1/purchase-orders/{orderId}/ack |
| A-11 | A_penetrate | ok |  |  |
| A-12 | A_penetrate | ok |  |  |
| A-13 | A_penetrate | ok |  |  |
| A-14 | A_penetrate | ok |  |  |
| A-15 | A_penetrate | ok |  |  |
| A-16 | A_penetrate | ok |  |  |
| B-01 | B_source | ok |  |  |
| B-02 | B_source | ok |  |  |
| B-03 | B_source | ok |  |  |
| B-04 | B_source | ok |  |  |
| B-05 | B_source | ok |  |  |
| B-06 | B_source | ok |  |  |
| B-07 | B_source | ok |  |  |
| B-08 | B_source | ok |  |  |
| C-01 | C_module_trap | ok |  |  |
| C-02 | C_module_trap | ok |  |  |
| C-03 | C_module_trap | ok |  |  |
| C-04 | C_module_trap | ok |  |  |
| C-05 | C_module_trap | ok |  |  |
| C-06 | C_module_trap | ok |  |  |
| C-07 | C_module_trap | ok |  |  |
| C-08 | C_module_trap | ok |  |  |
| D-01 | D_constraint | ok |  |  |
| D-02 | D_constraint | ok |  |  |
| D-03 | D_constraint | ok |  |  |
| D-04 | D_constraint | ok |  |  |
| E-01 | E_path_faithful | ok |  | /v1/purchase-orders |
| E-02 | E_path_faithful | ok |  | /v1/purchase-orders/{orderId} |
| E-03 | E_path_faithful | ok |  | /v1/purchase-orders/status |
| E-04 | E_path_faithful | ok |  | /v1/purchase-orders/{orderId}/ack |
