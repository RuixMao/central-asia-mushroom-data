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

test("server-renders the product homepage and secondary routes", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();
  assert.match(html, /因恒科技/);
  assert.match(html, /连接中国与中亚/);
  assert.match(html, /中亚农业数据终端/);
  assert.match(html, /市场机会平台/);
  assert.match(html, /href="\/terminal"/);
  assert.match(html, /href="\/data-assets"/);
  assert.match(html, /href="\/opportunities"/);
  assert.match(html, /href="\/services"/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape|react-loading-skeleton/i);

  const terminal = await render("/terminal");
  assert.equal(terminal.status, 200);
  assert.match(await terminal.text(), /中国出口.*中亚进口/);

  const assets = await render("/data-assets");
  assert.equal(assets.status, 200);
  const assetsHtml = await assets.text();
  assert.match(assetsHtml, /现有可用数据/);
  assert.match(assetsHtml, /现在没有，但确有商业价值的数据/);
});
