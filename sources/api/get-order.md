# Get purchase order

Original demo spec (not a vendor document).

`GET /v1/purchase-orders/{orderId}` returns one purchase order.

`orderId` is 8 alphanumeric characters. It is not an internal auto-increment id. PO 号 ≠ 内部 id.

Unknown ids return 404. This is not a shipment detail endpoint.
