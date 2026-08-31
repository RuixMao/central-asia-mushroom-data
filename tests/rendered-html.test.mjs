import assert from "node:assert/strict";
import test from "node:test";
import {marketReadiness} from "../app/market-readiness.ts";

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
  assert.match(html, /食用菌跨境市场数据与研究咨询/);
  assert.match(html, /海关贸易数据库/);
  assert.match(html, /电商零售监测/);
  assert.match(html, /市场与渠道研究/);
  assert.match(html, /定制研究咨询/);
  assert.doesNotMatch(html, /US\$4,647,430|14 泰铢\/包|Big C Online/);
  assert.match(html, /提交需求/);
  assert.match(html, /老挝/);
  assert.match(html, /东南亚/);
  assert.match(html, /找市场/);
  assert.match(html, /查行情/);
  assert.match(html, /市场洞察/);
  assert.match(html, /出海服务/);
  assert.match(html, /提交需求/);
  assert.match(html, /href="\/privacy"/);
  assert.match(html, /href="\/terms"/);
  assert.match(html, /href="\/market"/);
  assert.match(html, /近期值得关注的市场/);
  assert.match(html, /您现在要做什么/);
  assert.doesNotMatch(html, /重点国家|现在要完成哪项判断/);
  assert.match(html, /中亚/);
  assert.match(html, /东南亚/);
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

  const countries = await render("/insights/country?expand=LA");
  assert.equal(countries.status, 200);
  const countriesHtml = await countries.text();
  assert.match(countriesHtml, /比较目标市场/);
  assert.match(countriesHtml, /href="\/market"/);
  for (const code of ["LA", "VN", "TH", "MM", "KH", "KZ", "UZ", "KG", "TJ", "TM"]) {
    assert.match(countriesHtml, new RegExp(`href="/markets/${code}"`));
  }

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

test("country and case detail pages show traceable evidence", async () => {
  const laos = await render("/markets/LA");
  assert.equal(laos.status, 200);
  const laosHtml = await laos.text();
  assert.match(laosHtml, /鲜平菇 100g/);
  assert.match(laosHtml, /20,000 基普\/包/);
  assert.match(laosHtml, /Foodpanda Laos/);
  assert.match(laosHtml, /164,226\.7/);
  assert.doesNotMatch(laosHtml, /共 0 条价格观察|更新于 —/);

  const cases = await render("/expand/cases");
  assert.equal(cases.status, 200);
  const casesHtml = await cases.text();
  assert.match(casesHtml, /食用菌跨境项目案例库/);
  assert.doesNotMatch(casesHtml, /案例收集中/);

  const exportCases = await render("/expand/cases/export");
  assert.equal(exportCases.status, 200);
  const exportHtml = await exportCases.text();
  assert.match(exportHtml, /出口创汇超过390万美元/);
  assert.match(exportHtml, /查看原文/);
});

test("every target market appears in the customer decision journey", async () => {
  const codes = ["LA", "VN", "TH", "MM", "KH", "KZ", "UZ", "KG", "TJ", "TM"];
  const names = ["老挝", "越南", "泰国", "缅甸", "柬埔寨", "哈萨克斯坦", "乌兹别克斯坦", "吉尔吉斯斯坦", "塔吉克斯坦", "土库曼斯坦"];

  const tradeResponse = await render("/insights/trade");
  assert.equal(tradeResponse.status, 200);
  const tradeHtml = await tradeResponse.text();
  assert.match(tradeHtml, /全部市场/);
  assert.match(tradeHtml, /东南亚/);
  assert.match(tradeHtml, /中亚/);
  assert.match(tradeHtml, /各国最新可得年度/);
  assert.match(tradeHtml, /2025/);
  for (const name of names) assert.match(tradeHtml, new RegExp(name));

  const opportunitiesResponse = await render("/opportunities");
  assert.equal(opportunitiesResponse.status, 200);
  const opportunitiesHtml = await opportunitiesResponse.text();
  assert.match(opportunitiesHtml, /东南亚市场/);
  assert.match(opportunitiesHtml, /中亚市场/);
  for (let index = 0; index < codes.length; index += 1) {
    assert.match(opportunitiesHtml, new RegExp(`href="/markets/${codes[index]}"`));
    assert.match(opportunitiesHtml, new RegExp(names[index]));
  }

  const contactResponse = await render("/expand/contact");
  assert.equal(contactResponse.status, 200);
  const contactHtml = await contactResponse.text();
  for (const name of names) assert.match(contactHtml, new RegExp(name));

  const channelsResponse = await render("/insights/channels");
  assert.equal(channelsResponse.status, 200);
  const channelsHtml = await channelsResponse.text();
  for (const name of names) assert.match(channelsHtml, new RegExp(name));
});

test("country pages follow the objective readiness state machine",async()=>{
  const expected={LA:["L0",5,2],VN:["L1",1,1],TH:["L1",2,0],MM:["L2",0,0],KH:["L1",1,0],KZ:["L0",5,1],UZ:["L1",2,0],KG:["L2",0,0],TJ:["L2",0,0],TM:["L2",0,0]};
  for(const [code,[level,N,S]] of Object.entries(expected)){
    const response=await render(`/markets/${code}`);
    assert.equal(response.status,200);
    const html=(await response.text()).replaceAll("<!-- -->","");
    assert.match(html,new RegExp(`${level} ·`));
    assert.match(html,new RegExp(`N=${N} · S=${S}`));
    for(const section of ["价格","贸易","渠道","市场参考"])assert.match(html,new RegExp(section));
    assert.doesNotMatch(html,/共 0 条价格观察|更新于 —/);
  }
  const malaysia=marketReadiness([{grade:"B",species_id:"oyster_mushroom"},{grade:"C",species_id:"enoki"}]);
  assert.deepEqual({level:malaysia.level,N:malaysia.N,S:malaysia.S},{level:"L1",N:2,S:1});
});
