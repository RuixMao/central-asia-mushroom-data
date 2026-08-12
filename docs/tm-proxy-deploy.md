# tm-proxy 部署与启用（解决 TM 源在 CI 被 IP 屏蔽）

## 背景

`gipertm.com` / `asmanexpress.com`（土库曼斯坦价格源）在 GitHub Actions（美国数据中心 IP）
被目标站防火墙主动拒绝（`Connection refused`），但本地（中国网络）访问正常。
解决方式：用 Cloudflare Worker 做 HTTP 转发出口（Cloudflare 全球节点 IP），让 CI 也能采集。

## 一、部署 Worker（一次性，需 CF 账号）

1. 安装 wrangler（项目已带 `wrangler@4.92.0` 依赖）：
   ```bash
   npx wrangler login
   ```
2. 部署（配置文件 `wrangler.tm-proxy.toml`，入口 `worker/tm-proxy.js`）：
   ```bash
   npx wrangler deploy --config wrangler.tm-proxy.toml
   ```
   输出会给出 Worker 地址，形如 `https://tm-proxy.<subdomain>.workers.dev`。

> 也可在 Cloudflare Dashboard → Workers & Pages → 创建 Worker → 粘贴 `worker/tm-proxy.js` 内容，
> 然后 Deploy。两种方式等价。

## 二、CI 启用（GitHub Secrets）

1. GitHub 仓库 → Settings → Secrets and variables → Actions → New repository secret
2. 添加：`PROXY_BASE` = `https://tm-proxy.<subdomain>.workers.dev`
3. `daily-pipeline.yml` 已为 price collection 步骤预留 `PROXY_BASE: ${{ secrets.PROXY_BASE }}`，
   设置后下次运行自动生效；**未设置时保持直连**（本地/无代理环境不受影响）。

## 三、验证

- 本地测试代理链路（模拟 Worker 转发逻辑）：
  ```bash
  python -c "
  import requests, urllib3; urllib3.disable_warnings()
  r = requests.get('https://tm-proxy.<subdomain>.workers.dev/?url=' + 'https://gipertm.com/catalog/product/200763', timeout=20)
  print(r.status_code, 'NEXT_DATA' in r.text)
  "
  ```
- CI 验证：重跑 daily-pipeline，观察 fetch_price 日志中 gipertm/asmanexpress
  不再出现 `Connection refused`，有效条数应包含 TM 10 条。

## 安全说明

Worker 仅允许转发 `gipertm.com` / `asmanexpress.com` 两个白名单域名，防 SSRF；
响应带 CORS 头。无需任何密钥，公开部署即可。
