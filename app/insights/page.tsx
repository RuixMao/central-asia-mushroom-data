import ProductShell from "../product-shell";
import { mirrorRecords } from "../data";
import { InsightsLivePreview } from "../theme-live-data";
export const metadata={title:"需求分析｜食用菌出海服务平台"};

const countries = [["LA", "老挝"], ["VN", "越南"], ["TH", "泰国"], ["MM", "缅甸"], ["KH", "柬埔寨"], ["KZ", "哈萨克斯坦"], ["UZ", "乌兹别克斯坦"], ["KG", "吉尔吉斯斯坦"], ["TJ", "塔吉克斯坦"], ["TM", "土库曼斯坦"]] as const;
const money = (value: number) => value >= 1_000_000 ? `$${(value / 1_000_000).toFixed(2)}M` : `$${Math.round(value / 1_000).toLocaleString("en-US")}K`;

export default function Page() {
  return <ProductShell><main className="saas-main insight-landing">
    <section className="saas-hero compact"><span>DEMAND INSIGHTS</span><h1>食用菌出海需求分析</h1><p>以贸易规模、渠道价格与供应结构为核心，持续评估中亚与东南亚目标市场的品类需求和进入机会。</p></section>
    <section className="insight-brief" aria-label="研究摘要">
      <div><span>覆盖范围</span><strong>10 个目标市场</strong><small>中亚五国与东南亚五国</small></div>
      <div><span>核心口径</span><strong>3 类 HS 品类</strong><small>鲜冷、其他鲜菌与加工保藏</small></div>
      <div><span>更新体系</span><strong>日度 + 月度 + 年度</strong><small>渠道、官方统计与贸易基线互证</small></div>
    </section>
    <section className="insight-section-head"><div><span>COUNTRY COVERAGE</span><h2>目标市场概览</h2></div><p>分别展示各市场已经形成的贸易或公开价格信息。</p></section>
    <section className="country-research-grid">
      {countries.map(([code, name]) => { const rows = mirrorRecords.filter(row => row.countryCode === code); const total = rows.reduce((sum, row) => sum + Number(row.importerCifUsd ?? row.confirmedTradeUsd ?? 0), 0); const prices:Record<string,number>={LA:2,VN:7,TH:17,MM:2,KH:8}; const count=prices[code]??0; const grade = rows[0]?.confidence ?? (count?"已有价格":"持续更新"); return <article key={code} className={code === "LA" ? "featured" : ""}><header><span>{code}</span><em>{grade}</em></header><h3>{name}</h3><strong>{rows.length?money(total):count?`${count} 条报价`:"—"}</strong><p>{rows.length?`${rows.length} 个菌类贸易品类`:count?`已形成 ${count} 个商品价格记录`:"市场信息持续更新"}</p>{code === "LA" && <small>老挝优先补充贸易、物流与更多零售渠道</small>}<a href={`/terminal/${code}`}>查看国别研究 →</a></article>; })}
    </section>
    <InsightsLivePreview/>
    <section className="detail-card-grid insight-entry-grid">
      <article><span>国别需求</span><h2>目标市场需求画像</h2><p>按国家查看贸易、价格和供应结构。</p><a href="/insights/country">进入国别分析 →</a></article>
      <article><span>贸易分析</span><h2>规模与来源结构</h2><p>查看 HS 品类金额、来源构成和可信度。</p><a href="/insights/trade">进入贸易分析 →</a></article>
      <article><span>渠道地图</span><h2>平台与覆盖品类</h2><p>查看已纳入价格观察的公开渠道。</p><a href="/insights/channels">进入渠道地图 →</a></article>
    </section>
  </main></ProductShell>;
}
