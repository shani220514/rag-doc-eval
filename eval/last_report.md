<!-- kb hash: nogit  IndexId:   time: 2026-09-17T14:57:56.807067+08:00
     Recall@5 = not retrieve_miss / effective items with must_hit
     module accuracy = C-intent effective items without module_mixup
     path hallucination = illegal paths / extracted paths
-->
# RAG retrieve report

- git: nogit
- index_id: 
- started_at: 2026-09-17T14:57:56.807067+08:00
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
| A-01 | A_penetrate | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| A-02 | A_penetrate | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| A-03 | A_penetrate | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| A-04 | A_penetrate | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| A-05 | A_penetrate | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| A-06 | A_penetrate | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| A-07 | A_penetrate | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| A-08 | A_penetrate | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| A-09 | A_penetrate | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| A-10 | A_penetrate | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| A-11 | A_penetrate | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| A-12 | A_penetrate | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| A-13 | A_penetrate | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| A-14 | A_penetrate | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| A-15 | A_penetrate | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| A-16 | A_penetrate | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| B-01 | B_source | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| B-02 | B_source | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| B-03 | B_source | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| B-04 | B_source | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| B-05 | B_source | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| B-06 | B_source | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| B-07 | B_source | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| B-08 | B_source | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| C-01 | C_module_trap | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| C-02 | C_module_trap | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| C-03 | C_module_trap | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| C-04 | C_module_trap | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| C-05 | C_module_trap | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| C-06 | C_module_trap | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| C-07 | C_module_trap | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| C-08 | C_module_trap | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| D-01 | D_constraint | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| D-02 | D_constraint | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| D-03 | D_constraint | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| D-04 | D_constraint | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| E-01 | E_path_faithful | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| E-02 | E_path_faithful | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| E-03 | E_path_faithful | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
| E-04 | E_path_faithful | ok |  | pass | /v1/purchase-orders /v1/purchase-orders/{orderId} /v1/purchase-orders/status /v1/purchase-orders/{orderId}/ack |
