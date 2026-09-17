# List purchase orders

Original demo spec (not a vendor document).

`GET /v1/purchase-orders` returns purchase orders in a query window of at most 7 days, looking back at most 6 months.

Pagination uses `page_size` (default 50, maximum 200). `date_from` and `date_to` must be sent as a pair.

This endpoint is read-only. It is not the shipment list and not the sales-order list.
