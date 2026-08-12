# KZ / TM 数据源扩展记录

更新日期：2026-08-12。

| 国家 | 平台 | 结果 | 接入状态 |
|---|---|---|---|
| KZ | Kaspi | HTTP 200，商品由 JavaScript 渲染 | 已接入合规 Playwright 渲染适配器 |
| KZ | Arbuz | 当前环境 HTTP 403 | blocked，不绕过 |
| KZ | Flagma | HTTP 200，未发现可核验蘑菇报价 | gap |
| TM | Goshmak | SSL/网关失败 | blocked |
| TM | Flagma TM | 暂无可核验商品 | gap |

Kaspi 适配器仅访问公开搜索页，不使用账户、Cookie、验证码求解或访问控制绕过。渲染页面出现验证时返回 `render_blocked`；运行失败返回 `render_failed`；未发现带价格的菌类商品返回 `price_missing`。上述错误均作为采集缺口处理，不写 0。

离线 fixture 覆盖商品卡片标题、来源链接与 KZT 价格解析。CI 运行真实渲染前需要安装 Chromium：`python -m playwright install --with-deps chromium`。浏览器下载和页面渲染会增加约 1–3 分钟运行时间；后续应为渲染 HTML 增加按 URL/日期缓存。
