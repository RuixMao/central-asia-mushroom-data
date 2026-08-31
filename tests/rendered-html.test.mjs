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
  assert.match(html, /让食用菌出海决策有数据可依/);
  assert.match(html, /老挝/);
  assert.match(html, /越南/);
  assert.match(html, /柬埔寨/);
  assert.match(html, /选择目标市场/);
  assert.match(html, /查询当地价格/);
  assert.match(html, /验证市场机会/);
  assert.match(html, /了解出海步骤/);
  assert.match(html, /提交我的具体情况/);
  assert.match(html, /href="\/privacy"/);
  assert.match(html, /href="\/terms"/);
  assert.match(html, /href="\/market"/);
  assert.match(html, /目标市场价格速览/);
  assert.match(html, /全部市场/);
  assert.match(html, /全部国家/);
  assert.match(html, /中亚/);
  assert.match(html, /东南亚/);
  assert.match(html, /href="\/markets\/LA#prices"/);
  assert.doesNotMatch(html, /老挝（重点）|采集中/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape|react-loading-skeleton/i);

  const terminal = await render("/terminal");
  assert.equal(terminal.status, 200);
  const terminalHtml = await terminal.text();
  assert.match(terminalHtml, /食用菌出海数据终端/);
  assert.match(terminalHtml, /数据资产地图/);
  assert.match(terminalHtml, /按国家、品类和规格核对当地价格/);
  assert.match(terminalHtml, /当前可比较报价/);
  assert.match(terminalHtml, /近七次采集/);
  assert.match(terminalHtml, /导出当前结果 CSV/);
  assert.match(terminalHtml, /核算我的产品是否值得进入/);
  assert.match(terminalHtml, /每日 SKU 明细/);
  assert.match(terminalHtml, /来源/);

  const marketData = await render("/market-data");
  assert.equal(marketData.status, 200);
  const marketHtml = await marketData.text();
  assert.match(marketHtml, /菌业出海/);
  assert.match(marketHtml, /老挝/);
  assert.doesNotMatch(marketHtml, /老挝（重点）/);
  assert.match(marketHtml, /UN Comtrade/);
  assert.match(marketHtml, /456,800/);
  assert.match(marketHtml, /249,690/);
  assert.match(marketHtml, />A\+</);
  assert.match(marketHtml, /未报告/);
  assert.doesNotMatch(marketHtml, /正在使用已核验基线|多源数据已连接|置信度|单侧证据|发布门槛/);
  assert.match(marketHtml, /中国出口与目标市场进口对比/);

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
