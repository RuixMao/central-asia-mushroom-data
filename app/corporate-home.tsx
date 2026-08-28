import Image from "next/image";
import SiteNav from "./site-nav";
import MarketingFooter from "./marketing-footer";
import { countryOptions, mirrorRecords, opportunities } from "./data";

const money=(value:number)=>value>=1_000_000?`$${(value/1_000_000).toFixed(2)}M`:`$${Math.round(value/1000)}K`;
const market=(code:"KZ"|"UZ")=>{
  const rows=mirrorRecords.filter(x=>x.countryCode===code);
  const total=rows.reduce((sum,x)=>sum+Number(x.importerCifUsd??x.confirmedTradeUsd??0),0);
  const china=rows.reduce((sum,x)=>sum+Number(x.chinaFobUsd??0),0);
  return {rows,total,chinaShare:total?china/total*100:null,opportunity:opportunities.find(x=>x.countryCode===code)};
};
const focusMarkets=[{code:"KZ" as const,name:"哈萨克斯坦",conclusion:"规模领先，适合优先验证鲜品冷链与渠道成交条件。",risk:"冷链到岸成本及零售挂牌价与真实成交价差异"},{code:"UZ" as const,name:"乌兹别克斯坦",conclusion:"市场仍处培育期，适合从塔什干渠道和具体品类小范围验证。",risk:"批发成交、净重规格与进口来源国信息仍待核验"}];
const coverage=[
  ["KZ","已覆盖","今日覆盖","部分覆盖","3条参考价","部分覆盖"],
  ["UZ","已覆盖","今日覆盖","部分覆盖","待验证","部分覆盖"],
  ["KG","已覆盖","今日覆盖","部分覆盖","暂无来源","待验证"],
  ["TJ","镜像覆盖","今日覆盖","待验证","暂无来源","待验证"],
  ["TM","镜像覆盖","今日覆盖","待验证","暂无来源","待验证"],
];

export default function CorporateHome(){return <div className="marketing-site decision-home">
  <SiteNav/>
  <main>
    <section className="decision-hero"><div><span>中亚及东南亚食用菌市场判断与落地验证</span><h1>从老挝出发，寻找更合适的出海市场</h1><p>比较中亚五国与东南亚五国的市场规模、当地价格、渠道和进入风险，重点验证老挝，再决定是否报价、打样或试单。</p><div><a className="corp-primary" href="/insights/country">帮我选择目标市场</a><a className="corp-secondary" href="/market">查询当地价格 →</a></div><small className="hero-trust-note">结论均标明数据来源、更新时间和仍需核实的风险，不用缺失数据替您做决定。</small></div><Image src="/central-asia-corridor.png" alt="连接中国与中亚及东南亚市场的跨境贸易走廊" width={1536} height={1024} priority/></section>

    <section className="decision-section"><header><span>从您的问题开始</span><h2>现在最想解决哪一步？</h2></header><div className="decision-question-grid">{[["01","不知道先做哪个国家","比较市场规模、竞争、渠道和风险，缩小目标范围。","/insights/country","比较五国市场"],["02","不知道当地能卖多少钱","按国家、菌种、规格和渠道查看公开价格，判断报价空间。","/market","查询当地价格"],["03","担心机会无法真正落地","核对物流、准入、渠道和证据缺口，明确试单前还要验证什么。","/opportunities","查看待验证机会"]].map(x=><article key={x[0]}><span>{x[0]}</span><h3>{x[1]}</h3><p>{x[2]}</p><a href={x[3]}>{x[4]} →</a></article>)}</div></section>

    <section className="decision-section decision-capabilities"><header><span>您的下一步</span><h2>从初步判断走到实际行动</h2></header><div className="decision-capability-grid">{[["选择目标国家","先比较市场规模、竞争来源和进入风险","/insights/country","看看哪个国家更适合"],["判断价格空间","比较同类产品在不同城市和渠道的公开价格","/market","查询我的品类"],["核实关键风险","明确物流、准入和渠道成交还缺哪些证据","/opportunities","查看验证清单"],["获得针对性建议","围绕您的产品、产能和目标国家制定验证方案","/expand/contact","提交我的具体情况"]].map(x=><a href={x[2]} key={x[0]}><h3>{x[0]}</h3><p>{x[1]}</p><b>{x[3]} →</b></a>)}</div></section>

    <section className="decision-section" id="markets"><header><span>当前优先市场</span><h2>先从两个更值得关注的市场开始</h2><p>以下是基于现有贸易与价格信息的初步判断，不等于成交承诺；仍需结合您的产品成本和渠道条件验证。</p></header><div className="focus-market-grid">{focusMarkets.map(item=>{const data=market(item.code);return <article key={item.code}><div className="focus-market-title"><span>{item.code}</span><h3>{item.name}</h3><em>结论可信度较高</em></div><strong>{item.conclusion}</strong><dl><div><dt>已确认市场规模</dt><dd>{money(data.total)}</dd></div><div><dt>中国商品金额占比</dt><dd>{data.chinaShare==null?"—":`${data.chinaShare.toFixed(1)}%`}</dd></div><div><dt>值得关注的品类</dt><dd>{data.opportunity?.product??"—"}</dd></div></dl><p><b>您需要注意：</b>{item.risk}</p><p><b>建议先做：</b>{data.opportunity?.nextAction??"核实渠道报价、规格和价格依据"}</p><details><summary>数据如何得出？</summary><small>来自 UN Comtrade 2024 年进口申报，覆盖 HS 070951/200310；更新时间 2026-08-17。</small></details><a href={`/countries/${item.code.toLowerCase()}`}>看看这个市场是否适合我 →</a></article>})}</div></section>

    <section className="decision-section coverage-matrix-section"><header><span>信息是否足够</span><h2>哪些判断现在能做，哪些还要核实？</h2><p>信息越完整，越适合进入报价和试单；信息不足的市场只提供验证方向，不给出确定结论。</p></header><div className="coverage-matrix"><div className="coverage-matrix-row head"><b>国家</b><span>市场规模</span><span>公开价格</span><span>销售渠道</span><span>物流成本</span><span>进入要求</span></div>{coverage.map(row=><div className="coverage-matrix-row" key={row[0]}>{row.map((cell,i)=>i===0?<b key={cell}>{countryOptions.find(x=>x.code===cell)?.label}</b>:<span className={cell==="已覆盖"||cell==="今日覆盖"?"covered":cell==="暂无来源"?"missing":"partial"} key={`${row[0]}-${i}`}>{cell==="镜像覆盖"?"可参考伙伴国申报":cell==="今日覆盖"?"今天有公开价格":cell==="暂无来源"?"目前信息不足":cell==="待验证"?"需要进一步核实":cell}</span>)}</div>)}</div><small>信息状态更新于 2026-08-17。公开价格不等于真实成交价，物流与准入需按具体产品核实。</small></section>

    <section className="decision-action"><div><span>不知道下一步怎么选？</span><h2>告诉我们您的产品和目标，我们帮您整理验证清单</h2><p>您将知道应该先核实哪个国家、价格、渠道和风险，不必从大量数据中自己找答案。</p></div><div><a href="/expand/contact">提交我的具体情况</a><a href="/insights/country">先比较五国市场</a></div></section>
  </main>
  <MarketingFooter/>
</div>}
