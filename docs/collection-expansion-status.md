# 全产业链采集扩展状态

更新时间：2026-08-17

## 已接入

- KG：Globus、O!Market 搜索页多商品扫描；保留固定商品入口。单个搜索入口失败不会覆盖同平台已有成功状态。
- KZ / UZ / KG / TJ / TM：Flagma B2B 列表采集。只有明确价格进入价格候选；“价格面议”记录为 `gap / price_on_request`。
- Wildberries：公开搜索 API 多商品适配器。仅在 `WB_DESTS_JSON` 配置已核验国家配送区后启用，防止把其他国家商品误归入中亚。
- FAOSTAT：五国蘑菇与松露产量月度任务。保留官方 Flag；Flag I 写入 `is_estimate=true`。
- 来源健康：按平台写入候选数、有效数、待复核数、失败原因和观察日期。

## 本地验证结果

- Globus：固定入口取得 2 条候选；公开搜索页当前未返回可解析菌类商品，记录 `no_mushroom_products`，但不把整个平台误标为 gap。
- Flagma KZ：页面可访问，当前相关结果为价格面议，记录 `price_on_request`，不写 0。
- Wildberries：当前网络出口访问搜索 API 返回 429；适配器已就绪但不默认启用。
- Uzum：候选 API 当前返回站点 HTML 或 404，未接入正式价格源。
- FAOSTAT：当前本地网络读取超时；任务记录 `gap / unreachable`，不写 0 或估算值。

## 后续验证

- Arbuz：保留现有 JSON 解析器；尚未确认稳定公开商品 API 与真实商品 ID，因此不猜测 URL 接入。
- Korzinka、Magnum、Small、Narodny：需先确认稳定公开 API 或可持续列表页。
- OLX 多国：优先列表页；持续 403 的国家只登记缺口。
- 政策、企业与行业新闻：仅在具备发布日期、发布机构和原始链接时写入。
