# Acknowledge purchase order

Original demo spec (not a vendor document).

`POST /v1/purchase-orders/{orderId}/ack` is the write operation. Dashboards stay read-first: 看板以读为主.

Do not call this endpoint to acknowledge a shipment.
