# Codex 任务简报：攻克 KZ/TM 价格数据源（自动化，非人工补录）

> 用法：整段复制给 Codex 执行。执行前先 `git checkout -b feat/source-kz-tm`。
> 前置事实（2026-08-12 已实测）必须信任，不要重复全部侦察；可在你的执行环境里针对性复测网络。

---

```
你是资深数据工程师。任务：为本项目打通哈萨克斯坦（KZ）与土库曼斯坦（TM）的食用菌零售/批发价格自动采集——当前只有 KG/TJ/UZ 三个国家有自动价格源，KZ/TM 因平台反爬/JS 渲染为零。目标是不依赖人工补录，实现至少一个可行源，并保持现有"写 gap 不写 0、绝不伪造"的数据原则。

## 项目背景
- 技术栈：Python 采集管线（requests + BeautifulSoup）→ HTTP POST 写入 Cloudflare Sites（D1 数据库），GitHub Actions 每日调度
- 采集入口：pipeline/fetch_price.py（SOURCES 列表驱动，固定商品页直抓模式）
- 适配器：pipeline/adapters/ 下 base.py（通用解析基类）+ globus/omarket/zudbiyor/magnit/olx/somon 六个平台适配器
- 分类归一化：pipeline/taxonomy.py（17 菌种多语言字典、包装解析、每公斤价、USD 换算）
- 测试：tests/test_*.py（unittest 风格，用 tests/fixtures/ 离线页面样本，patch adapters.base.safe_get）
- 运行测试：python -m unittest discover -s tests -p 'test_*.py'

## 已完成侦察（2026-08-12 实测，勿重复大范围探测）
### 平台可达性矩阵（requests + 浏览器 UA）
| 国家 | 平台 | 结果 |
|---|---|---|
| KZ | kaspi.kz（最大电商） | 直连可达 HTTP 200，但**纯 JS SPA**：SSR 仅返回"请启用 JavaScript"，无商品数据；无公开免认证 API（yml 404） |
| KZ | arbuz.kz | 搜索页 404；api.arbuz.kz 连接失败；移动 API 401 需认证 |
| KZ | flagma.kz | HTTP 200 但搜索无结果（JS 渲染）；移动版 404 |
| KZ | carefood.kz | JSON API 返回空结果；small.kz/magnum.kz 连接失败 |
| TM | goshmak.com | HTTPS SSL 握手失败；HTTP 502；goshmak.com.tm 连接失败 |
| TM | flagma-tm.com | HTTP 200 但无蘑菇搜索结果 |
| TM | turkmenportal.com | 连接失败 |
| UZ | uzum.uz（参考） | 人机验证页（"Верификация"）；korzinka.uz 403 Cloudflare |
### 已验证失败的替代通道（勿重复投入）
- Jina Reader 渲染代理（r.jina.ai）：连接超时
- Numbeo 生活成本库：价格表 JS 异步加载（SSR 无蘑菇项）；API 需注册 key；prices_by_city 429 限流
- 搜索引擎当目录（Bing RSS / DuckDuckGo）：无结果或超时
### 网络环境注意
- 本机默认走代理 127.0.0.1:7890（可能未启动）：requests 用 session.trust_env=False 直连；pip/playwright 需 unset HTTP_PROXY/HTTPS_PROXY/ALL_PROXY
- Playwright 官方 CDN 下载失败 → 需设 PLAYWRIGHT_DOWNLOAD_HOST=https://cdn.npmmirror.com/binaries/playwright
- 已知可直连站点（requests 200）：kaspi.kz、arbuz.kz（首页）、flagma.kz、globus-online.kg、somon.tj、olx.uz、magnit.tj、zudbiyor.tj

## 解决方案路径（按优先级，任选一条跑通即达标；可组合）
1. **Playwright 无头浏览器渲染（推荐，确定性最高）**：Kaspi/arbuz/flagma 的 JS 渲染问题可被浏览器执行解决。新增 pipeline/adapters/render.py（渲染基类，sync_playwright + chromium headless，等待 networkidle/选择器后提取 innerText 或 HTML 交 BeautifulSoup 解析）；为 kaspi.kz 搜索页（https://kaspi.kz/shop/search/?text=шампиньон）写解析。注意：浏览器渲染慢且重，必须缓存渲染结果、限制并发、超时控制；CI 中可用 GitHub Actions 自带浏览器或加装。
2. **平台移动端/内部 API 逆向**：Kaspi PWA 的 XHR 端点（需 DevTools 抓包确认，如 /shop/api/search 或 graphql）；若找到免认证端点，直接用 requests 即可，比 Playwright 轻。
3. **官方开放接口**：Kaspi B2B API / arbuz 商户 API（需签约，商务流程；若走此路，代码上先留接口位）。
4. **聚合/二手源**：当地农业新闻、批发市场报价页（如 kazakhstan 农贸网站）——若发现固定页面含价格，走现有固定商品页模式即可。

## 执行步骤
1. 先在你的环境验证网络：能否直连 kaspi.kz/arbuz.kz/flagma.kz（requests trust_env=False）；能否安装 playwright 并下载 chromium（国内镜像）
2. 选定路径后写适配器（遵循 adapters/base.py 的 collect() 返回 (row, error) 或 (None, error) 约定，error 用代码如 price_missing/unreachable/render_failed）
3. 抓真实页面存 tests/fixtures/（渲染类可存渲染后的 HTML 片段），写离线单测（mock 网络，不得依赖在线渲染）
4. 接入 pipeline/fetch_price.py 的 SOURCES（平台 id 命名如 kaspi-kz、goshmak-tm；国家/城市/采集点字段与现有条目一致）
5. 跑通全量测试并提交

## 硬性约束（不可违反）
1. 不修改 app/api/**、db/、worker/、drizzle/、.github/ 现有工作流逻辑；不改 taxonomy.py 的返回契约
2. 不删除现有 6 个适配器与 SOURCES 中的 7 条配置
3. 数据原则：抓不到写 gap/错误码，绝不写 0、不伪造价格；渲染失败必须返回错误而非空值入库
4. 新增依赖（如 playwright）需同步更新 pipeline/requirements.txt，且说明 CI 影响（浏览器安装步骤）
5. 测试必须离线可跑（CI 无浏览器环境时，渲染适配器测试用 fixture 模拟渲染输出）
6. 每步保持 python -m compileall -q pipeline 通过

## 验收标准
1. python -m unittest discover -s tests -p 'test_*.py' 全绿（新增测试在内）
2. KZ 或 TM 至少一个国家有真实可用的自动采集源接入 SOURCES（提供当日实测证据：抓取结果含真实价格与来源 URL）
3. 若 Playwright 方案：提供渲染适配器 + kaspi 搜索页 fixture + 单测；若 API 方案：提供端点说明
4. fetch_price.py 覆盖矩阵：KZ≥1 或 TM≥1 新条目
5. 更新 docs/data-source-expansion.md 的侦察矩阵与接入记录
6. 分步 commit（feat(source): ...），最后报告：改了什么、验证了什么、还差什么

## 交付
- 新增/修改文件清单、新适配器解析逻辑说明、真实抓取样本证据（价格+URL）、测试结果输出、遗留风险（反爬稳定性、渲染耗时、CI 影响）
```

---

## 配套说明

- **为什么给 Codex 侦察矩阵**：这轮我已经把 uzum/korzinka/lalafo/tegen/goshmak/Jina/Numbeo/搜索引擎全验证过一遍（文档 docs/data-source-expansion.md 第五节有完整记录），Codex 拿到矩阵后直接跳过死胡同，聚焦 kaspi/arbuz 两条主线，能省掉一两个小时的无用探测。
- **Playwright 是重点**：kaspi.kz 直连可达（说明站点没封 IP），只是要执行 JS——浏览器渲染是目前唯一确定性的解。国内镜像 `cdn.npmmirror.com/binaries/playwright` 已实测是下载通道。
- **验收强调"离线可测"**：防止 Codex 写一个依赖在线渲染才能跑的测试，那样 CI 会挂。
- **风险提示**：反爬对抗是长期维护项，Kaspi 随时可能改版——所以 prompt 里要求把"渲染失败返回错误"写死，保持你们"写 gap 不写 0"的底线。
