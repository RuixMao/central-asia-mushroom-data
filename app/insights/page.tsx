import ProductShell from "../product-shell";
import { mirrorRecords } from "../data";

const countries = [["KZ", "哈萨克斯坦"], ["UZ", "乌兹别克斯坦"], ["KG", "吉尔吉斯斯坦"], ["TJ", "塔吉克斯坦"], ["TM", "土库曼斯坦"]] as const;
const money = (value: number) => value >= 1_000_000 ? `$${(value / 1_000_000).toFixed(2)}M` : `$${Math.round(value / 1_000).toLocaleString("en-US")}K`;

export default function Page() {
  return <ProductShell><main className="saas-main insight-landing">
    <section className="saas-hero compact"><span>DEMAND INSIGHTS</span><h1>中亚食用菌需求分析</h1><p>以贸易规模、渠道价格与供应结构为核心，持续评估中亚五国的品类需求、市场变化和进入机会。</p></section>
    <section className="insight-brief" aria-label="研究摘要">
      <div><span>研究范围</span><strong>中亚五国</strong><small>逐国呈现，不以缺报代替零值</small></div>
      <div><span>核心口径</span><strong>3 类 HS 品类</strong><small>鲜冷、其他鲜菌与加工保藏</small></div>
      <div><span>更新体系</span><strong>日度 + 月度 + 年度</strong><small>渠道、官方统计与贸易基线互证</small></div>
    </section>
    <section className="insight-section-head"><div><span>COUNTRY COVERAGE</span><h2>五国市场概览</h2></div><p>金额采用已确认的进口申报或伙伴国出口记录；右上角等级表示当前证据强度。</p></section>
    <section className="country-research-grid">
      {countries.map(([code, name]) => { const rows = mirrorRecords.filter(row => row.countryCode === code); const total = rows.reduce((sum, row) => sum + Number(row.importerCifUsd ?? row.confirmedTradeUsd ?? 0), 0); const grade = rows[0]?.confidence ?? "B"; return <article key={code} className={code === "UZ" ? "featured" : ""}><header><span>{code}</span><em>{grade}</em></header><h3>{name}</h3><strong>{money(total)}</strong><p>{rows.length} 个已确认菌类贸易品类</p>{code === "UZ" && <small>已覆盖官方贸易基线与塔什干渠道价格</small>}<a href={`/terminal/${code}`}>查看国别研究 →</a></article>; })}
    </section>
    <section className="detail-card-grid insight-entry-grid">
      <article><span>国别需求</span><h2>五国需求画像</h2><p>按国家查看贸易、价格和供应结构。</p><a href="/insights/country">进入国别分析 →</a></article>
      <article><span>贸易分析</span><h2>规模与来源结构</h2><p>查看 HS 品类金额、来源构成和可信度。</p><a href="/insights/trade">进入贸易分析 →</a></article>
      <article><span>渠道地图</span><h2>平台与覆盖品类</h2><p>查看已纳入价格观察的公开渠道。</p><a href="/insights/channels">进入渠道地图 →</a></article>
    </section>
  </main></ProductShell>;
}
