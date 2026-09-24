# 亚马逊DF订单客服知识库
> 文档说明：DF订单（Direct Fulfillment，亚马逊直接配送订单，卖家直发，亚马逊负责前台下单、售后客服），适用于客服/售后人员快速查询规则、问题排查、话术参考。
> 版本：V1.0
> 更新日期：2026-09-24

## 目录
1. 基础概念
2. DF订单核心规则
3. 订单状态释义
4. 常见问题分类&排查方案
5. 售后场景处理流程
6. 禁做事项&风险红线
7. 客服标准话术模板
8. 常见报错/申诉入口
9. 术语表

---

## 1. 基础概念
### 1.1 什么是DF订单
Direct Fulfillment（DF）：**买家在亚马逊前台下单，订单推送至卖家，由卖家仓库直接打包发货，亚马逊负责前端客服、退款、退货审核**。
> 区别：FBA是亚马逊仓库发货；DF是卖家自发货，归属亚马逊DF渠道，需遵守亚马逊DF时效、标签、物流要求。

### 1.2 DF订单特点
- 订单来源：亚马逊前台，买家账号为亚马逊买家
- 履约主体：卖家负责拣货、打包、贴标、发货、物流追踪
- 客服主体：亚马逊前台客服优先承接买家咨询；卖家后台接收DF工单处理
- 指标考核：订单准时发货率、有效追踪率、取消率、迟发率、缺陷率，直接影响DF权限

### 1.3 卖家侧入口
- 订单查看：亚马逊后台 > Orders > Direct Fulfillment Orders
- 工单处理：Direct Fulfillment Case / Concession Hub（理赔/让步单）
- 报表：DF履约指标报表、DF退货报表

---

## 2. DF订单核心规则
### 2.1 时效要求（关键）
1. **确认发货（Ship Confirm）**：订单推送后必须在规定SLA内标记发货，上传有效的物流追踪号
2. **备货时效**：DF订单一般要求**24小时内处理（工作日）**，节假日以亚马逊通知为准
3. **配送时效**：需满足前台展示的配送时效，超时会触发买家索赔、自动退款
> ⚠️ DF订单**不能随意取消**，无合理原因取消会拉高取消率，严重会关闭DF权限

### 2.2 面单&包装要求
- 必须使用亚马逊DF标签（订单内下载），不能用普通自发货标签
- 外箱不能出现其他平台logo，包装符合亚马逊包装标准
- 装箱单：按DF要求放置，部分站点禁止放卖家联系方式

### 2.3 物流要求
- 使用亚马逊认可承运商，追踪号必须可在亚马逊系统识别
- 追踪号必须真实，禁止虚拟单号、重复单号
- 丢失/破损：物流责任由卖家先行承担，卖家再向物流商索赔

### 2.4 退货规则
DF退货：买家发起退货请求，亚马逊审核退货标签，买家寄回**卖家仓库**（不是亚马逊仓）
- 买家退货地址：卖家配置的DF退货地址
- 收到退货后：卖家验货，在规定时限内处理退款；商品损坏/缺失，可提交证据拒绝全额退款

---

## 3. 订单状态释义
| 订单状态 | 说明 | 客服动作 |
| ---- | ---- | ---- |
| Unshipped | 未发货，新订单已推送卖家 | 尽快拣货打包，按时ship confirm |
| Shipped | 已标记发货，追踪号上传 | 监控物流轨迹，处理买家物流查询 |
| Delivered | 已签收 | 留意买家少件、破损、未收到工单 |
| Cancelled | 订单已取消 | 核查取消原因；亚马逊主动取消/买家取消，区分责任 |
| Return Requested | 买家发起退货申请 | 等待亚马逊审核退货单，准备接收退货 |
| Return Received | 卖家已收到退回包裹 | 验货，在时效内退款或拒退 |
| Concession | 让步单（理赔单） | 查看Concession Hub，核对索赔理由，提交抗辩证据 |

---

## 4. 常见问题分类&排查方案
### 4.1 订单类：找不到DF订单
**现象**：后台订单列表看不到DF订单，但买家说已下单
排查步骤：
1. 确认切换到DF订单视图（Direct Fulfillment Orders，不是普通自发货）
2. 核对站点、订单时间范围
3. 检查订单是否被亚马逊提前取消
4. 查看通知：订单是否因为库存不足被系统拦截
5. 如仍无：提交DF支持工单，提供买家订单号查询

### 4.2 库存不足无法发货
处理原则：**禁止直接取消订单**
1. 优先：联系亚马逊DF客服工单，说明库存短缺，申请订单延期
2. 备选：协商买家是否接受替换商品；买家不同意，则申请亚马逊协助取消，留存工单记录
> ❌ 风险：卖家私自取消DF订单 → 取消率飙升，DF权限暂停

### 4.3 物流未更新/追踪号无效
排查：
1. 确认单号录入正确，无空格、大小写错误
2. 确认承运商属于亚马逊DF认可物流商
3. 联系物流商确认是否已揽收；未揽收及时更新
4. 超过48h无轨迹：提前在工单备注，预防买家A-to-Z或Concession索赔

### 4.4 买家反馈未收到货（LTR）
排查流程：
1. 查询物流轨迹：是否显示Delivered
    - 已显示签收：核对签收地址、门卫/驿站代收，截图轨迹作为证据
    - 在途丢失：联系物流开丢失证明
2. 在Concession Hub查看是否生成理赔单
3. 收集证据：物流截图、签收记录，在规定时效内抗辩

### 4.5 买家收到商品破损/少件
1. 引导买家提供：照片（外包装+商品破损图、装箱照片）
2. 判断方案：部分退款 / 补发 / 退货退款
3. 所有协商结果，**必须在亚马逊DF工单内留痕**，不要私下微信/邮件承诺退款
> 私下退款不受平台保护，仍会产生Concession索赔

---

## 5. 售后场景处理流程
### 5.1 DF工单处理通用流程
1. 接收亚马逊转发的买家工单（DF Case）
2. 在SLA时效内响应（一般24h内回复）
3. 核实订单信息、物流、商品情况
4. 给出解决方案，上传证据（截图、照片）
5. 提交回复，持续跟进直到工单关闭
6. 归档记录，用于后续指标复盘

### 5.2 退货处理流程
1. 亚马逊审核买家退货请求，生成退货标签
2. 买家寄回商品至卖家DF退货地址
3. 包裹签收登记，开箱验货，拍照留存
4. ✅完好无损：全额退款
5. ⚠️商品损坏/缺失：整理验货照片，提交拒退理由，等待亚马逊裁决
6. 完成退款后，关闭退货工单

### 5.3 Concession让步单（理赔单）处理流程
> Concession：亚马逊先行赔付买家，然后向卖家追偿
1. 进入Concession Hub查看索赔原因、金额、截止抗辩时间
2. 收集抗辩证据：物流签收截图、打包视频、沟通工单记录
3. 在截止时间前提交抗辩；超时未提交 → 自动扣款
4. 抗辩成功：撤销扣款；失败：扣款生效，可进一步申诉
5. 复盘：记录原因优化履约（打包、物流、时效）

---

## 6. 禁做事项&风险红线
❌ 严禁行为：
1. 禁止私自取消DF订单，无亚马逊工单记录的取消会严重影响指标
2. 禁止上传虚假物流追踪号
3. 禁止引导买家离开亚马逊平台沟通（微信、独立站、电话私下交易）
4. 禁止在包裹内放卖家联系方式、营销卡片，诱导好评
5. 禁止不处理Concession让步单，超时自动扣款
6. 禁止承诺平台以外的售后保障（私下补偿、线下退款）

⚠️ 高风险指标：迟发率、订单取消率、有效追踪率、缺陷率，任一超标可直接暂停/关闭DF履约权限。

---

## 7. 客服标准话术模板
> 说明：所有回复使用英文，在亚马逊工单内回复；简洁，附证据链接/截图。

### 模板1：买家咨询发货进度
> We have received your DF order. The package has been picked up by carrier, tracking number: {trackingNo}. You can check the delivery updates on Amazon order page. We will monitor the shipment. Please let us know if you have further questions.

### 模板2：买家反馈商品破损
> Sorry for the damaged item. Could you please share photos of the outer package and defective product? After we receive the photos, we can offer options including partial refund, replacement or return.

### 模板3：买家说未收到货（已显示签收）
> According to carrier tracking, the package was delivered to {address} on {date}. It may be left with front desk / neighbor / parcel locker. Please help check. If you still cannot locate it, we will work with Amazon to investigate.

### 模板4：库存不足，申请延期（工单发给亚马逊DF客服）
> DF Order ID: {orderId}. Current inventory temporary out of stock. We request order shipment delay. Estimated available date: {date}. We will ship immediately once stock available.

### 模板5：Concession抗辩（已签收证据）
> Concession ID:{concessionId}. Tracking shows delivered on {date} to buyer address. Attached carrier delivery screenshot as proof. Buyer claimed non-receipt but parcel was successfully delivered. Request to reverse this concession charge.

---

## 8. 常见报错/申诉入口
1. DF订单无法标记发货：后台DF Support Case，检查追踪号格式、承运商配置
2. Concession扣款申诉：Concession Hub对应单据内提交抗辩
3. DF履约指标告警：后台Performance > DF Metrics，开绩效工单申诉
4. DF权限被暂停：DF绩效支持工单，提交整改计划

---

## 9. 术语表
| 缩写 | 全称 | 释义 |
| ---- | ---- | ---- |
| DF | Direct Fulfillment | 亚马逊直接配送订单（卖家直发） |
| Concession | Concession | 让步单，亚马逊先行赔付买家，向卖家追偿 |
| SLA | Service Level Agreement | 平台要求响应/履约时限 |
| LTR | Lost in Transit | 物流丢件 |
| Ship Confirm | 确认发货 | 卖家上传追踪号标记已发货 |
| A-to-Z | A-to-Z Guarantee | 亚马逊买家保障索赔 |
