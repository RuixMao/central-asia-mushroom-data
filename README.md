# vinext-starter

A clean full-stack starter running on
[vinext](https://github.com/cloudflare/vinext), with optional Cloudflare D1 and
Drizzle support.

## Prerequisites

- Node.js `>=22.13.0`

## Quick Start

```bash
npm install
npm run dev
npm run build
```

This starter does not use `wrangler.jsonc`.

## Included Shape

- edit site code under `app/`
- `.openai/hosting.json` declares optional Sites D1 and R2 bindings
- `vite.config.ts` simulates declared bindings for local development
- `db/schema.ts` starts intentionally empty
- `examples/d1/` contains an optional D1 example surface
- `drizzle.config.ts` supports local migration generation when needed

## Workspace Auth Headers

Signed-in visitors receive both `oai-authenticated-user-id` and `oai-authenticated-user-email`. Private Sites require every visitor to sign in; public Sites may also have anonymous visitors, for whom neither header is present.

The user ID is stable for the same user on the same Site and different across Sites. Email and name are intended for display or contact purposes.

SIWC-authenticated workspace sites may also receive
`oai-authenticated-user-full-name` when the user's SIWC profile has a non-empty
`name` claim. The full-name value is percent-encoded UTF-8 and is accompanied by
`oai-authenticated-user-full-name-encoding: percent-encoded-utf-8`.

Treat the full name as optional and fall back to email when it is absent:

```tsx
import { headers } from "next/headers";

export default async function Home() {
  const requestHeaders = await headers();
  const userId = requestHeaders.get("oai-authenticated-user-id");
  const email = requestHeaders.get("oai-authenticated-user-email");
  const encodedFullName = requestHeaders.get("oai-authenticated-user-full-name");
  const fullName =
    encodedFullName &&
    requestHeaders.get("oai-authenticated-user-full-name-encoding") ===
      "percent-encoded-utf-8"
      ? decodeURIComponent(encodedFullName)
      : null;

  const displayName = fullName ?? email;
  // ...
}
```

## Optional Dispatch-Owned ChatGPT Sign-In

Import the ready-to-use helpers from `app/chatgpt-auth.ts` when the site needs
optional or required ChatGPT sign-in:

- Use `getChatGPTUser()` for optional signed-in UI.
- Use `requireChatGPTUser(returnTo)` for server-rendered pages that should send
  anonymous visitors through Sign in with ChatGPT.
- Use `chatGPTSignInPath(returnTo)` and `chatGPTSignOutPath(returnTo)` for
  browser links or actions.
- Pass a same-origin relative `returnTo` path for the destination after sign-in
  or sign-out. The helper validates and safely encodes it.
- Mark protected pages with `export const dynamic = "force-dynamic"` because
  they depend on per-request identity headers.

Dispatch owns `/signin-with-chatgpt`, `/signout-with-chatgpt`, `/callback`, the
OAuth cookies, and identity header injection. Do not implement app routes for
those reserved paths. Routes that do not import and call the helper remain
anonymous-compatible.

SIWC establishes identity only; it does not prove workspace membership. Use the
Sites hosting platform's access policy controls for workspace-wide restrictions,
or enforce explicit server-side membership or allowlist checks.

Use SIWC for account pages, user-specific dashboards, saved records, and write
actions tied to the current ChatGPT user. Leave public content anonymous.

## Useful Commands

- `npm run dev`: start local development
- `npm run build`: verify the vinext build output
- `npm test`: build the starter and verify its rendered loading skeleton
- `npm run db:generate`: generate Drizzle migrations after schema changes

## Learn More

- [vinext Documentation](https://github.com/cloudflare/vinext)
- [Drizzle D1 Guide](https://orm.drizzle.team/docs/get-started/d1-new)

## 自动化数据管线

`pipeline/` 每日采集中亚五国及东南亚五国的 UN Comtrade 贸易、汇率与市场背景数据，并采集当地商超、电商和分类信息价格；东南亚任务优先验证老挝。所有结果写入 D1；无价格时写入 `status: gap`，绝不写 0。随后生成中文市场日报并写入报告表。

核心入口：

- `python pipeline/fetch_trade.py`：最近两年、十国、3 个 HS 编码。
- `python pipeline/fetch_laos_trade.py`：低调用量抓取老挝进口申报及中、越、泰出口镜像，分别写入官方市场规模和伙伴国镜像下限。
- `.github/workflows/laos-price.yml`：老挝在线商超价格独立优先采集，每日三次检查万象渠道；仅将品种、价格和规格完整的商品写入正式价格口径。
- `python pipeline/fetch_logistics.py`：中亚核心路线时效中位数。
- `python pipeline/fetch_sea_logistics.py`：登记东南亚五国官方通道、口岸和运输方式；取得可追溯承运报价前不写时效或运价。
- `python pipeline/fetch_price.py`：按 `pipeline/config.py` 的 `COUNTRIES` 与 `pipeline/fetch_price.py` 的 `SOURCES` 采集价格和来源缺口。
- `python pipeline/generate_report.py`：读取最新快照并生成日报。

价格采集内置自动复核闭环：先按页面证据校验品类、规格、价格和合理区间；
可由同批有效样本解释的小包装溢价会自动复核通过，仍缺少可验证证据的记录
不会写入正式价格表；同日已经存在的旧记录也会被撤回，失败原因只留在采集审计
和来源质量统计中。定时任务下一轮会重新读取源页面，证据恢复后重新进入正式库，
因此不会长期堆积为“待复核”。如需观察旧行为，可临时设置
`AUTO_REVIEW_QUARANTINE=0`。

站点环境变量：`CRON_SECRET`、`UN_COMTRADE_API_KEY`，可选 `DEPLOY_HOOK_URL`。GitHub Actions Secrets：`SITE_URL`、`CRON_SECRET`、`UN_COMTRADE_API_KEY`、`AI_PROVIDER`、`AI_API_KEY`。

首次启用：

```bash
npm run db:generate
npm run build
```

Sites 部署会根据 `.openai/hosting.json` 的 `DB` 绑定创建/连接 D1，并应用 `drizzle/` 迁移。手动运行 GitHub Actions 的 **Daily Data Pipeline** 可立即测试；`include_prices` 控制是否同时执行周频价格采集。
