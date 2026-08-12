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

## UZ / TM 应对策略（2026-08-12 补充）

### 乌兹别克斯坦（UZ）
- **OLX.uz**：唯一已接入源，但 2026-08-12 起被 IP 级 403 封锁（本机 UA/Referer/cookie 预热均无法绕过；CI IP 或可通，时通时断）。**保留但不作为唯一依赖**。
- **Yandex Market UZ**（market.yandex.uz / m.market.yandex.uz）：HTTP 200 可达，1.5MB SSR 壳，但商品列表由 JS 异步加载（静态请求拿不到商品，菌词仅在 UI/SEO 文案中）。**已新增 YandexMarketAdapter（渲染源）**：复用 RenderedProductAdapter，渲染后从 body 文本提取"含菌词 + N сум"片段；CI 已装 Playwright，真实效果待首次运行验证（失败走 gap，不写 0）。
- **UZ 官方统计**：api.siat.stat.uz 有蘑菇**产量**数据（2018-2024，PDF，供给侧）——可作为生产/供给指标入库（metric=production），但**无零售价格发布**。
- 策略：OLX（静态，尽力而为）+ Yandex（渲染，待验证）双源冗余；若 Yandex 渲染也被验证页拦截，下一步走其移动 API 逆向或人工维护固定商品页。

### 土库曼斯坦（TM）—— 2026-08-12 已突破 ✅

**结论更新：TM 已有 2 个可核验自动价格源（gipertm + asmanexpress），6 条固定商品页。**

| 平台 | 方式 | 蘑菇商品 | 实测价格 |
|---|---|---|---|
| **Giper.tm**（gipertm.com） | HTTP 直抓 + `__NEXT_DATA__` JSON | 5 条（Tokaýçy 300/800gr、Esmo 腌制 400gr、Ra-Ra 切片 400gr、RITA 400gr） | 29 / 79.5 / 21.5 / 24.5 / 22.5 TMT |
| **Asman Express**（asmanexpress.com） | HTTP 直抓 + `__NEXT_DATA__` JSON | 1 条（Eyran komelek 1000gr 新鲜） | 68 TMT |

- **突破关键**：两个站都是 Next.js，商品数据内嵌 `<script id="__NEXT_DATA__">` JSON，**纯 HTTP 直抓即可**（不需要 Playwright 渲染，CI 直接可跑）。gipertm 的搜索/分类 API 需认证（401），但固定商品详情页免认证且 SSR 内嵌价格。
- **汇率**：config.py `FX_TO_CNY` 已有 TMT=2.04（与公开汇率 1 TMT≈2.02 CNY 一致）。
- **taxonomy 更新**：补土库曼语同义词（şampinýon/şampinon/şampion → button_mushroom；kömelek/gömelek/komelek → AMBIGUOUS 泛称）、FORM 腌渍/罐装土库曼语变体（marinadlanan/konserw）、parse_package 支持 `gr` 单位。
- **诚实处理**：`Eyran komelek`（泛称蘑菇）species=unknown 不强行归双孢菇；gipertm 5 条多为罐装/腌制（400-800gr），价格按包装归一化；新鲜/罐装状态由 product_form 标记。
- **历史死路（已排除）**：halk.market（302→Instagram）、halkmarket.org（DNS 无记录）、goshmak（失联）、turkmenportal（路由阻断）、stat.gov.tm（可达但无零售价）。TM 电商此前"不可达"是因站点多托管于 TM 本地网络，而 gipertm/asmanexpress 托管于海外（95.85.126.x / 93.171.223.x）绕开了隔离。
