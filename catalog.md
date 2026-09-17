# Demo corpus catalog

示例语料是仓库内自写的**虚构采购订单 API**。与 Amazon、Alibaba 或任何雇主产品无隶属关系。

Sample knowledge is a **fictional** purchase-order API. It is not affiliated with
Amazon, Alibaba, or any employer product.

| File | Role | 角色 | Synced |
|------|------|------|--------|
| `cards/purchase-order.md` | Layered knowledge card | 分层知识卡 | yes |
| `sources/api/list-orders.md` | List endpoint spec | 列表接口说明 | yes |
| `sources/api/get-order.md` | Detail endpoint spec | 详情接口说明 | yes |
| `sources/api/order-status.md` | Status endpoint spec | 状态接口说明 | yes |
| `sources/api/acknowledge.md` | Ack write spec | 确认写接口说明 | yes |

只有 `cards/**/*.md` 和 `sources/**/*.md` 允许进入同步范围。`.env`、评测报告、密钥形态会被 `sync_guard` 拦截。
