# Demo corpus catalog

Sample knowledge is a **fictional** purchase-order API. It is not affiliated with
Amazon, Alibaba, or any employer product.

| File | Role | Synced |
|------|------|--------|
| `cards/purchase-order.md` | Layered knowledge card | yes |
| `sources/api/list-orders.md` | List endpoint spec | yes |
| `sources/api/get-order.md` | Detail endpoint spec | yes |
| `sources/api/order-status.md` | Status endpoint spec | yes |
| `sources/api/acknowledge.md` | Ack write spec | yes |

Only `cards/**/*.md` and `sources/**/*.md` may be uploaded. `.env`, eval reports, and secrets are blocked by `sync_guard`.
