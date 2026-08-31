import ProductShell from "../product-shell";
import { dataSources, mirrorRecords, opportunities, productionEvidence, tradeRecords } from "../data";
import LivePriceSummary from "./live-price-summary";
import LivePriceInventory from "./live-price-inventory";

const money=(value:number|null)=>value==null?"—":value>=1_000_000?`$${(value/1_000_000).toFixed(2)}M`:`$${Math.round(value/1000)}K`;

export const metadata={title:"数据中心｜食用菌出海服务平台"};

export default function DataCenterPage(){
  const total=mirrorRecords.reduce((sum,row)=>sum+Number(row.importerCifUsd??row.confirmedTradeUsd??0),0);
  const countries=new Set(mirrorRecords.map(row=>row.countryCode)).size;
  const latestTrade=tradeRecords.filter(row=>row.y2024!=null).sort((a,b)=>Number(b.y2024)-Number(a.y2024)).slice(0,6);
  const signals=opportunities.filter(item=>item.status!=="暂缓").slice(0,3);
  return <ProductShell><main className="saas-main data-center-page">
    <section className="saas-hero compact"><span>市场数据</span><h1>判断一个市场是否值得进入</h1><p>查看市场规模、当地供给、公开价格、销售渠道和进入条件。</p></section>

    <section className="data-center-kpis">
      <article><span>已确认贸易规模</span><strong>{money(total)}</strong><small>2024 年；UN Comtrade 与伙伴国镜像</small></article>
      <article><span>贸易覆盖</span><strong>{countries}/10 国</strong><small>按进口国申报与伙伴国镜像分层展示</small></article>
      <LivePriceInventory mode="kpis"/>
    </section>

    <section className="data-center-block"><header><div><span>01 · TRADE</span><h2>贸易规模与品类结构</h2><p>先看市场容量，再进入国别、来源国和镜像差异核验。</p></div><a href="/insights/trade">查看完整贸易分析 →</a></header><div className="data-center-table"><div className="head"><b>国家</b><b>HS / 品类</b><b>2024 进口额</b><b>数据状态</b></div>{latestTrade.map(row=><div key={`${row.countryCode}-${row.hs}`}><span>{row.country}</span><span>{row.hs} · {row.product}</span><strong>{money(row.y2024)}</strong><em>已确认</em></div>)}</div></section>

    <section className="data-center-split">
      <article><span>02 · 本土供给</span><h2>本土供给与进口依赖</h2><p>结合农业供给基线与进口规模，评估当地供给能力和外部采购空间。</p><dl><div><dt>中亚来源</dt><dd>FAOSTAT 与当地生产记录</dd></div><div><dt>东南亚来源</dt><dd>FAO 老挝市场资料与进口价格参考</dd></div></dl><a href="/data-assets">查看数据口径 →</a></article>
      <LivePriceSummary/>
    </section>

    <section className="data-center-block"><header><div><span>LOCAL PRODUCTION EVIDENCE</span><h2>FAOSTAT 未收录国家的生产证据</h2><p>企业实际产出、规划产能与出口状态分开保存；以下记录均不替代国家年度总产量。</p></div></header><div className="data-center-table"><div className="head"><b>国家</b><b>证据类型</b><b>数量 / 状态</b><b>统计处理</b></div>{productionEvidence.map((row,index)=><div key={`${row.countryCode}-${row.type}-${index}`}><span>{row.country}<small>{row.source}</small></span><span>{row.type}</span><strong>{row.value}</strong><em>{row.status}｜{row.note}</em></div>)}</div></section>

    <section className="data-center-block"><header><div><span>04 · PRODUCT SCAN</span><h2>新品类与产品形态</h2><p>查看已进入目标市场公开渠道的品类、规格和产品形态。</p></div><a href="/market/scan">进入品类扫描 →</a></header><LivePriceInventory mode="species"/></section>

    <section className="data-center-block"><header><div><span>05 · SIGNALS</span><h2>需求信号与决策参考</h2><p>结合贸易变化与价格观察，识别值得进一步核验的市场机会。</p></div><a href="/opportunities">查看全部商机 →</a></header><div className="data-signal-grid">{signals.map(item=><article key={item.id}><small>{item.country} · HS {item.hs}</small><h3>{item.product}</h3><strong>{item.status}</strong><p>{item.signal}</p><b>建议关注：{item.nextAction}</b></article>)}</div></section>

    <section className="data-center-split">
      <article><span>07 · CORRIDOR & ACCESS</span><h2>贸易通道、物流与准入</h2><p>围绕具体产品核对线路报价、运输时效、报关要求和市场准入条件。</p><div className="data-status-row"><span>政策要求：按品类查询</span><span>线路成本：按路线询价</span><span>产品准入：逐项核验</span></div><a href="/expand/contact">提交验证需求 →</a></article>
    </section>

    <section className="data-center-block"><header><div><span>DATA SOURCES</span><h2>来源、频率与可信度</h2><p>官方统计、伙伴国镜像和公开市场观察分层使用，避免把不同口径混为一谈。</p></div><a href="/data-assets">查看平台能力 →</a></header><div className="data-source-grid">{dataSources.map(source=><article key={source.name}><div><strong>{source.name}</strong><em>{source.level}</em></div><p>{source.scope} · {source.cadence}</p><small>{source.status}｜{source.note}</small></article>)}</div></section>
  </main></ProductShell>;
}
