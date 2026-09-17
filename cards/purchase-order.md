---
id: purchase-order
module: PO
aliases: [采购订单, Purchase Order]
not_this: [Shipment, Sales Order]
---

## 导读

本卡只讲采购订单（Purchase Order）。发运与销售订单不是本卡。
文档入口：文档站「采购订单」章节。列表页打开即拉数，无需点搜索。

## 列表接口

列表 `GET /v1/purchase-orders`。查询窗 ≤7 天，最多回看 6 个月。分页 `page_size` 默认 50、上限 200。`date_from` 与 `date_to` 必须成对。

## 详情接口

详情 `GET /v1/purchase-orders/{orderId}`。单号 8 位字母数字。PO 号 ≠ 内部 id。

## 状态接口

状态 `GET /v1/purchase-orders/status`。查询窗 ≤7 天。返回 accepted、rejected、pending。

## 确认接口

写操作 `POST /v1/purchase-orders/{orderId}/ack`。看板以读为主。

## 已知坑

发运与销售订单不是本卡。窗口两边不一致；PO 号 ≠ 内部 id；`date_from` 与 `date_to` 必须成对。

## 相关链接

发运 API、发票 API 只挂链接，正文不展开。
