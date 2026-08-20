import ProductShell from "../product-shell";
import { dataSources, mirrorRecords, opportunities, priceObservations, productionEvidence, tradeRecords } from "../data";

const money=(value:number|null)=>value==null?"—":value>=1_000_000?`$${(value/1_000_000).toFixed(2)}M`:`$${Math.round(value/1000)}K`;

export const metadata={title:"数据中心｜中亚食用菌出海服务平台"};

export default function DataCenterPage(){
  const total=mirrorRecords.reduce((sum,row)=>sum+Number(row.importerCifUsd??row.confirmedTradeUsd??0),0);
  const countries=new Set(mirrorRecords.map(row=>row.countryCode)).size;
  const products=new Set(priceObservations.map(row=>row.product)).size;
  const channels=new Set(priceObservations.map(row=>row.source)).size;
  const latestTrade=tradeRecords.filter(row=>row.y2024!=null).sort((a,b)=>Number(b.y2024)-Number(a.y2024)).slice(0,6);
  const signals=opportunities.filter(item=>item.status!=="暂缓").slice(0,3);
  return <ProductShell><main className="saas-main data-center-page">
    <section className="saas-hero compact"><span>全部市场依据</span><h1>用哪些信息判断一个市场值不值得进入？</h1><p>从市场规模、当地供给、公开价格、销售渠道和进入条件逐项核对。建议先看结论，再按需要查看这里的完整依据。</p></section>

    <section className="data-center-kpis">
      <article><span>已确认贸易规模</span><strong>{money(total)}</strong><small>2024 年；UN Comtrade 与伙伴国镜像</small></article>
      <article><span>贸易覆盖</span><strong>{countries}/5 国</strong><small>塔吉克斯坦、土库曼斯坦为镜像口径</small></article>
      <article><span>已核验市场品类</span><strong>{products} 类</strong><small>来自公开挂牌价观察</small></article>
      <article><span>价格来源组合</span><strong>{channels} 组</strong><small>同一组合可能包含多个公开渠道</small></article>
    </section>

    <section className="data-center-block"><header><div><span>01 · TRADE</span><h2>贸易规模与品类结构</h2><p>先看市场容量，再进入国别、来源国和镜像差异核验。</p></div><a href="/insights/trade">查看完整贸易分析 →</a></header><div className="data-center-table"><div className="head"><b>国家</b><b>HS / 品类</b><b>2024 进口额</b><b>数据状态</b></div>{latestTrade.map(row=><div key={`${row.countryCode}-${row.hs}`}><span>{row.country}</span><span>{row.hs} · {row.product}</span><strong>{money(row.y2024)}</strong><em>已确认</em></div>)}</div></section>

    <section className="data-center-split">
      <article><span>02 · LOCAL SUPPLY</span><h2>本土供给与进口依赖</h2><p>结合农业供给基线与进口规模，评估当地供给能力和外部采购空间。</p><dl><div><dt>数据来源</dt><dd>FAOSTAT + 当地生产证据</dd></div><div><dt>数据口径</dt><dd>未收录≠零产量 · 计划值单列</dd></div></dl><a href="/data-assets">查看数据口径 →</a></article>
      <article><span>03 · PRICES</span><h2>当地市场行情</h2><p>按原币、规格、城市、渠道和观察日期比较公开挂牌价。</p><dl><div><dt>价格样本</dt><dd>{priceObservations.length} 条已核验记录</dd></div><div><dt>重点市场</dt><dd>阿拉木图 / 塔什干</dd></div></dl><a href="/market/prices">查看价格明细 →</a></article>
    </section>

    <section className="data-center-block"><header><div><span>LOCAL PRODUCTION EVIDENCE</span><h2>FAOSTAT 未收录国家的生产证据</h2><p>企业实际产出、规划产能与出口状态分开保存；以下记录均不替代国家年度总产量。</p></div></header><div className="data-center-table"><div className="head"><b>国家</b><b>证据类型</b><b>数量 / 状态</b><b>统计处理</b></div>{productionEvidence.map((row,index)=><div key={`${row.countryCode}-${row.type}-${index}`}><span>{row.country}<small>{row.source}</small></span><span>{row.type}</span><strong>{row.value}</strong><em>{row.status}｜{row.note}</em></div>)}</div></section>

    <section className="data-center-block"><header><div><span>04 · PRODUCT SCAN</span><h2>新品类与产品形态</h2><p>查看已进入中亚公开渠道的品类、规格和产品形态。</p></div><a href="/market/scan">进入品类扫描 →</a></header><div className="data-chip-list">{Array.from(new Set(priceObservations.map(row=>row.product))).map(name=><span key={name}>{name}</span>)}</div></section>

    <section className="data-center-block"><header><div><span>05 · SIGNALS</span><h2>需求信号与决策参考</h2><p>结合贸易变化与价格观察，识别值得进一步核验的市场机会。</p></div><a href="/opportunities">查看全部商机 →</a></header><div className="data-signal-grid">{signals.map(item=><article key={item.id}><small>{item.country} · HS {item.hs}</small><h3>{item.product}</h3><strong>{item.status}</strong><p>{item.signal}</p><b>建议关注：{item.nextAction}</b></article>)}</div></section>

    <section className="data-center-split">
      <article><span>06 · CHANNELS</span><h2>当地销售渠道</h2><p>按国家、平台和覆盖品类寻找适合进一步接洽的市场渠道。</p><a href="/insights/channels">查看渠道地图 →</a></article>
      <article><span>07 · CORRIDOR & ACCESS</span><h2>贸易通道、物流与准入</h2><p>围绕具体产品核对线路报价、运输时效、报关要求和市场准入条件。</p><div className="data-status-row"><span>政策要求：按品类查询</span><span>线路成本：按路线询价</span><span>产品准入：逐项核验</span></div><a href="/expand/contact">提交验证需求 →</a></article>
    </section>

    <section className="data-center-block"><header><div><span>DATA SOURCES</span><h2>来源、频率与可信度</h2><p>官方统计、伙伴国镜像和公开市场观察分层使用，避免把不同口径混为一谈。</p></div><a href="/data-assets">查看平台能力 →</a></header><div className="data-source-grid">{dataSources.map(source=><article key={source.name}><div><strong>{source.name}</strong><em>{source.level}</em></div><p>{source.scope} · {source.cadence}</p><small>{source.status}｜{source.note}</small></article>)}</div></section>
  </main></ProductShell>;
}
