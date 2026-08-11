import assert from "node:assert/strict";
import test from "node:test";

async function render(path = "/") {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request(`http://localhost${path}`, { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the corporate website and public data center", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();
  assert.match(html, /因恒科技/);
  assert.match(html, /inhen-tech-logo\.png/);
  assert.match(html, /洞察中亚市场/);
  assert.match(html, /产品与服务/);
  assert.match(html, /数据中心/);
  assert.match(html, /解决方案/);
  assert.match(html, /市场洞察/);
  assert.match(html, /申请产品演示/);
  assert.match(html, /href="\/privacy"/);
  assert.match(html, /href="\/terms"/);
  assert.match(html, /href="\/market-data"/);
  assert.match(html, /\$6\.96M/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape|react-loading-skeleton/i);

  const terminal = await render("/terminal");
  assert.equal(terminal.status, 200);
  const terminalHtml = await terminal.text();
  assert.match(terminalHtml, /中亚菌类数据终端/);
  assert.match(terminalHtml, /数据资产地图/);
  assert.match(terminalHtml, /先用已有数据建立事实底座/);

  const marketData = await render("/market-data");
  assert.equal(marketData.status, 200);
  const marketHtml = await marketData.text();
  assert.match(marketHtml, /中亚菌类市场/);
  assert.match(marketHtml, /UN Comtrade/);
  assert.match(marketHtml, /72\.1%/);
  assert.match(marketHtml, /未报告/);
});
