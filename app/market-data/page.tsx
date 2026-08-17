import Link from "next/link";
import ProductShell from "../product-shell";
import PriceLiveTable from "./price-live-table";
import MirrorLiveGrid from "./mirror-live-grid";

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

const prices = [
  ["阿拉木图", "鲜双孢菇", "电商 / 商超", "2,730–3,300 ₸/kg", "2026-08"],
  ["阿拉木图", "鲜平菇", "批发", "1,300–1,500 ₸/kg", "2026-08"],
  ["塔什干", "鲜双孢菇", "电商 / 零售", "60,000–78,000 苏姆/kg", "2026-07～08"],
  ["塔什干", "腌制双孢菇 430ml", "电商平台", "25,990 苏姆/罐", "2026-08"],
];

export default function MarketDataPage() {
  return <ProductShell><div className="data-site">
    <main>
      <section className="data-hero"><span>YINHENG MARKET DATA</span><h1>中亚菌类市场<br />公开市场数据</h1><p>将官方贸易、农业生产与市场挂牌信息按统一字段整理，并保留来源、时间、统计口径和缺失状态。</p><div><b>数据基线：2022–2024</b><b>页面更新：2026-08-10</b><b>覆盖：中亚五国</b></div></section>
      <nav className="data-subnav"><Link href="/market-data/trade">贸易数据</Link><Link href="/market-data/prices">价格数据</Link><Link href="/market-data/trade-baseline">贸易数据集说明</Link><Link href="/market-data/retail-prices">价格数据集说明</Link></nav>
      <section className="data-summary"><article><span>2024 已报告进口额</span><strong>$6.96M</strong><small>重点菌类 HS 合计</small></article><article><span>贸易记录</span><strong>9 组</strong><small>国家 × HS 编码</small></article><article><span>镜像差异提示</span><strong>2 项</strong><small>差异率超过 70%</small></article><article><span>公开价格记录</span><strong>4 条</strong><small>哈萨克斯坦、乌兹别克斯坦</small></article></section>
      <section className="data-block" id="trade"><div className="data-heading"><div><span>01 · TRADE BASELINE</span><h2>重点菌类进口基线</h2></div><p>金额为美元。未报告值保持缺失，不以 0 替代。</p></div><div className="market-table"><div className="market-row market-head"><b>报告国</b><b>HS</b><b>商品</b><b>2022</b><b>2023</b><b>2024</b></div>{trade.map(row => <div className="market-row" key={row[0] + row[1]}>{row.map((cell, i) => <span className={cell === "未报告" ? "missing" : ""} key={i}>{cell}</span>)}</div>)}</div><p className="data-footnote">来源：UN Comtrade 年度公开数据基线；进口额为报告国 CIF 口径。</p></section>
      <section className="data-block pale" id="mirror"><div className="data-heading"><div><span>02 · TRADE COMPARISON</span><h2>中国出口与中亚进口对比</h2></div><p>按国家和菌类品类展示 2024 年公开贸易金额，并以 A+、A、B+、B 标注资料完整度。</p></div><MirrorLiveGrid /><p className="data-footnote">A+ 表示进口国公布了金额、数量和来源国；B+ 表示已汇总两个或以上伙伴国的出口申报。金额均为美元。</p></section>
      <section className="data-block" id="price"><div className="data-heading"><div><span>03 · MARKET PRICE</span><h2>食用菌价格监测</h2></div><p>展示可核验的市场挂牌价；默认以美元结算，可按实时汇率切换人民币。挂牌价不等同于实际成交价。</p></div><PriceLiveTable /></section>
      <section className="data-sources" id="sources"><div><span>04 · DATA SOURCES</span><h2>数据来源</h2><p>贸易、生产和价格信息来自各国官方机构及国际数据库，并保留发布日期和统计口径，便于复核。</p></div><div><a href="https://english.customs.gov.cn/Statistics/Statistics" target="_blank" rel="noreferrer"><b>01</b><span>中国海关统计<small>中国与中亚五国进出口数据</small></span></a><a href="https://www.stat.tj/ru/" target="_blank" rel="noreferrer"><b>02</b><span>塔吉克斯坦国家统计局<small>对外贸易及国内市场统计</small></span></a><a href="https://stat.gov.tm/en" target="_blank" rel="noreferrer"><b>03</b><span>土库曼斯坦国家统计委员会<small>外贸、农业和国内贸易统计</small></span></a><a href="https://comtradeapi.un.org" target="_blank" rel="noreferrer"><b>04</b><span>联合国商品贸易数据库<small>各国贸易数据的统一查询与比较</small></span></a><a href="https://www.fao.org/faostat" target="_blank" rel="noreferrer"><b>05</b><span>联合国粮农组织数据库<small>农业生产与供给结构</small></span></a></div></section>
      <section className="data-cta"><div><span>NEXT STEP</span><h2>需要完整数据、字段字典或专项研究？</h2></div><Link href="/expand/contact">申请完整数据 →</Link></section>
    </main>
  </div></ProductShell>;
}
