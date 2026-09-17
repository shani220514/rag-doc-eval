# Purchase order status

Original demo spec (not a vendor document).

`GET /v1/purchase-orders/status` returns status rows in a query window of at most 7 days.

Status values: accepted, rejected, pending.

This is not a shipment tracking feed.
