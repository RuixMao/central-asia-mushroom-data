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
  assert.match(html, /中亚食用菌出海/);
  assert.match(html, /市场行情/);
  assert.match(html, /需求分析/);
  assert.match(html, /解决方案/);
  assert.match(html, /出海路径/);
  assert.match(html, /合作对接/);
  assert.match(html, /href="\/privacy"/);
  assert.match(html, /href="\/terms"/);
  assert.match(html, /href="\/market"/);
  assert.match(html, /\$6\.00M/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape|react-loading-skeleton/i);

  const terminal = await render("/terminal");
  assert.equal(terminal.status, 200);
  const terminalHtml = await terminal.text();
  assert.match(terminalHtml, /中亚菌类数据终端/);
  assert.match(terminalHtml, /数据资产地图/);
  assert.match(terminalHtml, /每日食用菌细分品类价格终端/);
  assert.match(terminalHtml, /筛选内有效报价/);
  assert.match(terminalHtml, /近七次采集/);
  assert.match(terminalHtml, /导出当前结果 CSV/);
  assert.match(terminalHtml, /定制数据与 API/);
  assert.match(terminalHtml, /每日 SKU 明细/);
  assert.match(terminalHtml, /来源/);

  const marketData = await render("/market-data");
  assert.equal(marketData.status, 200);
  const marketHtml = await marketData.text();
  assert.match(marketHtml, /中亚菌类市场/);
  assert.match(marketHtml, /UN Comtrade/);
  assert.match(marketHtml, /456,800/);
  assert.match(marketHtml, /249,690/);
  assert.match(marketHtml, />A\+</);
  assert.match(marketHtml, /未报告/);
  assert.doesNotMatch(marketHtml, /正在使用已核验基线|多源数据已连接|置信度|单侧证据|发布门槛/);
  assert.match(marketHtml, /中国出口与中亚进口对比/);

  const reports = await render("/reports");
  assert.equal(reports.status, 200);
  const reportsHtml = await reports.text();
  assert.match(reportsHtml, /YINHENG RESEARCH/);
  assert.match(reportsHtml, /数据来源：因恒科技/);
  assert.doesNotMatch(reportsHtml, /AI 生成|AI 报告|DeepSeek/);

  const reportDetail = await render("/reports/example-report");
  assert.equal(reportDetail.status, 200);
  assert.match(await reportDetail.text(), /正在读取报告/);

  const encodedReportDetail = await render("/reports/%E4%B8%AD%E4%BA%9A%E8%8F%8C%E7%B1%BB%E6%97%A5%E6%8A%A5");
  assert.equal(encodedReportDetail.status, 200);
  assert.match(await encodedReportDetail.text(), /正在读取报告/);
});
