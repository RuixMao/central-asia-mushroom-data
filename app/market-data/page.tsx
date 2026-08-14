import Link from "next/link";
import ProductShell from "../product-shell";
import PriceLiveTable from "./price-live-table";

const trade = [
  ["哈萨克斯坦", "070951", "鲜、冷蘑菇（伞菌属）", "$8,893,873", "$3,181,278", "$4,193,266"],
  ["哈萨克斯坦", "200310", "加工保藏蘑菇", "$4,412,358", "$1,644,872", "$1,027,970"],
  ["哈萨克斯坦", "070959", "其他鲜蘑菇", "$510,974", "$426,093", "$409,221"],
  ["乌兹别克斯坦", "070951", "鲜、冷蘑菇（伞菌属）", "$15,930", "$488,375", "$456,804"],
  ["乌兹别克斯坦", "200310", "加工保藏蘑菇", "$69,233", "$111,800", "$68,204"],
  ["吉尔吉斯斯坦", "070951", "鲜、冷蘑菇（伞菌属）", "$9,994", "$40,966", "$40,376"],
  ["吉尔吉斯斯坦", "070959", "其他鲜蘑菇", "$97,554", "$246,088", "$535,916"],
  ["吉尔吉斯斯坦", "200310", "加工保藏蘑菇", "$130,482", "$130,030", "$228,842"],
  ["塔吉克斯坦", "200310", "加工保藏蘑菇", "$39,358", "$119,104", "未报告"],
];

const mirrors = [
  ["哈萨克斯坦", "HS 200310", "$1,027,970", "$3,688,137", "72.1%", "显著差异"],
  ["吉尔吉斯斯坦", "HS 070951", "$40,376", "$31,321", "22.4%", "低基数"],
  ["吉尔吉斯斯坦", "HS 200310", "$228,842", "$64,386", "71.9%", "显著差异"],
];

const prices = [
  ["阿拉木图", "鲜双孢菇", "电商 / 商超", "2,730–3,300 ₸/kg", "2026-08"],
  ["阿拉木图", "鲜平菇", "批发", "1,300–1,500 ₸/kg", "2026-08"],
  ["塔什干", "鲜双孢菇", "电商 / 零售", "60,000–78,000 苏姆/kg", "2026-07～08"],
  ["塔什干", "腌制双孢菇 430ml", "电商平台", "25,990 苏姆/罐", "2026-08"],
];

export default function MarketDataPage() {
  return <ProductShell><div className="data-site">
    <main>
      <section className="data-hero"><span>YINHENG MARKET DATA</span><h1>中亚菌类市场<br />公开数据样例</h1><p>将官方贸易、农业生产与市场挂牌信息按统一字段整理，并保留来源、时间、统计口径和缺失状态。</p><div><b>数据基线：2022–2024</b><b>页面更新：2026-08-10</b><b>覆盖：中亚五国</b></div></section>
      <section className="data-summary"><article><span>2024 已报告进口额</span><strong>$6.96M</strong><small>重点菌类 HS 样例合计</small></article><article><span>贸易记录</span><strong>9 组</strong><small>国家 × HS 编码</small></article><article><span>镜像差异提示</span><strong>2 项</strong><small>差异率超过 70%</small></article><article><span>市场价格样例</span><strong>4 条</strong><small>哈萨克斯坦、乌兹别克斯坦</small></article></section>
      <section className="data-block" id="trade"><div className="data-heading"><div><span>01 · TRADE BASELINE</span><h2>重点菌类进口基线</h2></div><p>金额为美元。未报告值保持缺失，不以 0 替代。</p></div><div className="market-table"><div className="market-row market-head"><b>报告国</b><b>HS</b><b>商品</b><b>2022</b><b>2023</b><b>2024</b></div>{trade.map(row => <div className="market-row" key={row[0] + row[1]}>{row.map((cell, i) => <span className={cell === "未报告" ? "missing" : ""} key={i}>{cell}</span>)}</div>)}</div><p className="data-footnote">来源：UN Comtrade 年度公开数据基线；进口额为报告国 CIF 口径。</p></section>
      <section className="data-block pale" id="mirror"><div className="data-heading"><div><span>02 · MIRROR CHECK</span><h2>中国出口 × 中亚进口交叉核验</h2></div><p>镜像差异用于发现统计口径、转口与链路问题，不直接代表损失或市场空间。</p></div><div className="mirror-grid">{mirrors.map(([country, hs, cif, fob, gap, status]) => <article key={country + hs}><span>{country} · {hs}</span><div><p>进口方 CIF<b>{cif}</b></p><p>中国出口 FOB<b>{fob}</b></p></div><strong>{gap}<small>镜像差异率</small></strong><i>{status}</i></article>)}</div><p className="data-footnote">差异率 = |进口方 CIF − 中国出口 FOB| ÷ max（两者）；低金额样本单独标记“低基数”。</p></section>
      <section className="data-block" id="price"><div className="data-heading"><div><span>03 · MARKET PRICE</span><h2>食用菌价格监测</h2></div><p>展示可核验的市场挂牌价，并统一折算为人民币参考价；挂牌价不等同于实际成交价。</p></div><PriceLiveTable /></section>
      <section className="data-sources" id="sources"><div><span>04 · SOURCES & METHODOLOGY</span><h2>数据来源与可信度</h2><p>每条记录保留来源、采集日期与口径说明。官方统计优先作为基线，行业资料和市场挂牌用于补充验证。</p></div><div><a href="https://comtradeapi.un.org" target="_blank" rel="noreferrer"><b>A</b><span>UN Comtrade<small>官方贸易统计与镜像口径</small></span></a><a href="https://www.fao.org/faostat" target="_blank" rel="noreferrer"><b>A−</b><span>FAOSTAT<small>农业生产统计；估计值另行标注</small></span></a><a href="https://umdis.org" target="_blank" rel="noreferrer"><b>B</b><span>行业与市场资料<small>用于供给结构和渠道佐证</small></span></a><Link href="/#contact"><b>B+</b><span>市场挂牌采集<small>多来源比对，不等同成交价</small></span></Link></div></section>
      <section className="data-cta"><div><span>NEXT STEP</span><h2>需要完整数据、字段字典或专项研究？</h2></div><Link href="/#contact">申请数据样例 →</Link></section>
    </main>
  </div></ProductShell>;
}
