/**
 * tm-proxy — Cloudflare Worker 中转代理
 *
 * 用途：gipertm.com / asmanexpress.com 在 GitHub Actions（美国数据中心 IP）被
 * 目标站防火墙主动拒绝（Connection refused），而本地（中国网络）访问正常。
 * 本 Worker 作为 HTTP 转发出口（Cloudflare 全球节点），让 CI 也能采集 TM 价格源。
 *
 * 部署：wrangler deploy（需 CF 账号；见 docs/tm-proxy-deploy.md）
 * 启用：GitHub 仓库 Secrets 添加 PROXY_BASE=https://<your-worker>.workers.dev
 *       （daily-pipeline.yml 已预留该环境变量，未设置则保持直连）
 *
 * 安全：仅允许转发白名单域名，禁止 SSRF 到任意目标。
 */
const ALLOWED_HOSTS = ["gipertm.com", "asmanexpress.com"];

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const target = url.searchParams.get("url");
    if (!target) {
      return new Response("missing url param", { status: 400 });
    }
    let t;
    try {
      t = new URL(target);
    } catch {
      return new Response("invalid url", { status: 400 });
    }
    const host = t.hostname;
    const allowed = ALLOWED_HOSTS.some((d) => host === d || host.endsWith("." + d));
    if (!allowed) {
      return new Response(`host not allowed: ${host}`, { status: 403 });
    }
    try {
      const resp = await fetch(target, {
        headers: {
          "User-Agent": "Mozilla/5.0 YinhengMarketResearch/1.0 (+data-source-audit)",
          "Accept-Language": "ru-RU,ru;q=0.9,tk;q=0.8",
        },
        redirect: "follow",
      });
      const headers = new Headers(resp.headers);
      headers.set("Access-Control-Allow-Origin", "*");
      headers.set("Access-Control-Allow-Methods", "GET, OPTIONS");
      return new Response(resp.body, { status: resp.status, headers });
    } catch (err) {
      return new Response(`proxy error: ${err.message}`, { status: 502 });
    }
  },
};
