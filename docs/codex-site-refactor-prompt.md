# Codex 任务简报：统一「中亚菌类数据平台」站点信息架构

> 用法：把【详细版】整段复制给 Codex 执行；如果只要快速收敛，用文末【精简版】。
> 执行前建议先 `git checkout -b refactor/site-ia` 开分支。

---

## 【详细版】（推荐）

```
你是资深前端/全栈工程师。请重构本仓库（Cloudflare vinext + React 19 App Router + Drizzle）的站点导航与页面组织。当前站点存在 5 套互不连通的布局体系，需要收敛为清晰的两级信息架构，同时保证不破坏任何 API 路由与数据管线。

## 背景
- 技术栈：vinext (Cloudflare Sites)、React 19、App Router 风格、Tailwind 4、Drizzle + D1
- 构建与测试：npm run build（构建）、npm test（构建后渲染测试）、npm run dev（开发）
- 项目根：仓库根目录，以相对路径操作

## 现状问题（已核实，含证据）
1. 五套独立布局体系并存、导航互不连通：
   - corp-site（app/corporate-home.tsx）：仅首页 / 使用，自建 corp-nav 锚点导航 + corp-footer，品牌用 inhen-tech-logo.png
   - data-site（app/market-data/page.tsx）：仅 /market-data 使用，自建 data-nav/data-footer，只有「返回官网」链接
   - intel-app（app/terminal/page.tsx）：仅 /terminal 使用，自建左侧边栏 intel-side + intel-top
   - saas-site（app/product-shell.tsx）：被 6 页复用（/catalog /reports /docs /pricing /dashboard /dataset/[slug]），saas-nav + saas-footer，「枢」字标
   - marketing-site（app/site-nav.tsx + app/marketing-footer.tsx）：/opportunities /data-assets /services /solutions/[slug]，「枢」字标 + CENTRAL ASIA DATA
2. 品牌标识不一致：logo 图与「枢」字标混用；产品名「中亚菌业数据终端」/「中亚菌类数据终端」/「因恒智能」混用
3. 遗留无引用组件：app/dashboard.tsx（447 行「指挥台」五大板块）与配套 app/data.ts，已 grep 确认无任何 import
4. 法律页 app/privacy/page.tsx、app/terms/page.tsx 为裸页面（无导航，仅「← 返回首页」）
5. 样式全部散落在 app/globals.css（.corp-* / .data-* / .intel-* / .saas-* / .marketing-* 前缀并存）

## 目标架构（两级结构，共享一套全站顶部导航 + 页脚）
- 官网/营销层：/、/market-data、/solutions/*、/services、/opportunities、/data-assets、/pricing、/privacy、/terms
- 产品/数据层：/terminal、/catalog、/reports、/docs、/dashboard、/dataset/*
- 全站导航建议项：首页 · 数据中心 · 数据终端 · 数据目录 · AI 报告 · API · 定价 · 账户后台；营销入口（解决方案/服务/商机/数据资产）收敛为「更多/洞察」下拉或保留在首页与页脚

## 执行步骤（每步独立 commit，先 Step 1 再逐级推进）
### Step 1 统一导航组件
- 以 app/product-shell.tsx 为唯一基础，重构为共享布局组件（可保留 ProductShell 命名），顶部导航扩展为覆盖上表全部路由
- 删除 app/site-nav.tsx、app/marketing-footer.tsx 中的重复导航定义，改为复用新组件（或删除文件后统一接入）
### Step 2 迁移页面套用统一布局
- market-data/page.tsx：移除自建 data-nav/data-footer，套用统一导航；页面主体视觉保留（globals.css 中 .data-* 类保留）
- terminal/page.tsx：保留应用型左侧边栏 intel-side 与 30 秒轮询看板逻辑，但顶部品牌区与全站统一
- corporate-home.tsx：首页保留营销 hero/产品/洞察等视觉区块，导航与全站统一（锚点滚动可保留，链接与统一导航对齐）
- opportunities / data-assets / services / solutions/[slug]：将 SiteNav+MarketingFooter 替换为统一导航
### Step 3 统一品牌标识
- 全站 logo 统一为 inhen-tech-logo.png（推荐）或统一「枢」字标，二选一，不得混用
- 产品名统一为「因恒科技 · 中亚菌类数据平台」（或你判断最一致的一种），同步修改 globals.css 相关样式
### Step 4 清理遗留
- 再次 grep 确认无引用后，删除 app/dashboard.tsx 与 app/data.ts；若 data.ts 中仍有被引用导出，仅删除 dashboard.tsx 并最小化 data.ts
### Step 5 法律页与细节
- privacy/terms 套用统一布局（最小页脚即可）
- 修正任何 import 位置异常（如 site-nav.tsx 中 import 在文件底部的情况）

## 硬性约束（不可违反）
1. 不修改 app/api/** 任何路由；不修改 db/、pipeline/、worker/、drizzle/、package.json、next.config.ts
2. 不删除任何现有页面路由（只改布局与导航，页面仍可访问）；遗留清理仅限确认无引用的文件
3. 复用 globals.css 既有 class，允许新增少量样式，不得推翻现有视觉风格
4. 每步改动后 npm run build 必须成功；全部完成后 npm test 必须通过

## 验收标准
1. npm run build && npm test 全部通过
2. 可达性走查：从任意页面经顶部导航可到达任意其他页面（至少走查 首页→数据中心→数据终端→数据目录→AI报告→API→定价→账户→法律页 这条链路）
3. 全站品牌标识一致，无混用
4. grep 复核：无 >100 行的无引用遗留组件
5. 视觉不突兀：各页面主体视觉与现有一致，仅导航/页脚/品牌变化

## 交付
- 每个 Step 一个 git commit，提交信息格式如：refactor(site): unify navigation across all pages
- 完成后在回复中列出：改动文件清单、删除文件清单、最终导航结构、验证命令与结果
```

---

## 【精简版】（快速收敛时用）

```
重构站点导航与页面组织。本项目（Cloudflare vinext + React 19）现有 5 套互不连通的布局体系：corp-site（app/corporate-home.tsx 首页）、data-site（app/market-data/page.tsx）、intel-app（app/terminal/page.tsx 侧边栏）、saas-site（app/product-shell.tsx，已被 /catalog /reports /docs /pricing /dashboard /dataset/* 复用）、marketing-site（app/site-nav.tsx + app/marketing-footer.tsx，被 /opportunities /data-assets /services /solutions/* 使用）。品牌标识与产品名混用；app/dashboard.tsx（447行）与 app/data.ts 是无引用遗留；app/privacy、app/terms 是裸页面。

请执行：
1. 以 app/product-shell.tsx 为唯一基础，做一套覆盖全站所有路由的统一顶部导航 + 页脚
2. 各页面移除自建导航：market-data 去掉 data-nav/data-footer；terminal 保留左侧边栏但顶部品牌统一；opportunities/data-assets/services/solutions 换用统一导航；首页 corporate-home 保留营销视觉但导航与全站一致
3. 全站 logo 统一为 inhen-tech-logo.png，产品名统一为「因恒科技 · 中亚菌类数据平台」
4. 确认无引用后删除 app/dashboard.tsx 与 app/data.ts
5. privacy/terms 套用统一最小布局

硬性约束：不改 app/api/**、db/、pipeline/、worker/、package.json；不删除任何现有页面路由；复用 globals.css 既有样式；每步 npm run build 必须通过，完成后 npm test 必须通过。分步 commit（refactor(site): ...）。完成后报告改动清单、删除清单、导航结构与验证结果。
```

---

## 配套说明（给执行者/你自己）

- **为什么以 product-shell 为基础**：它已被 6 页复用，是唯一"成体系"的布局，改造面最小；其余体系各只有 1 页，迁移成本低。
- **终端页是应用型界面**：保留侧边栏是合理的（类似控制台），只需统一顶部品牌，不要强行套营销导航。
- **风险点**：globals.css 里 .corp-* 与 .saas-* 有大量样式，迁移时用"组件级替换"而非"全局重写"，避免一次改动过大破坏视觉。
- **回滚方案**：每步独立 commit，若某步验收失败，`git revert` 该步即可，不影响其他步骤。
