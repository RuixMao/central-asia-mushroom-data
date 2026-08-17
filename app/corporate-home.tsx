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
const focusMarkets=[{code:"KZ" as const,name:"哈萨克斯坦",conclusion:"规模领先，适合优先验证鲜品冷链与渠道成交条件。",risk:"冷链到岸成本及零售挂牌价与真实成交价差异"},{code:"UZ" as const,name:"乌兹别克斯坦",conclusion:"市场仍处培育期，适合从塔什干渠道和具体品类小范围验证。",risk:"批发成交、净重规格与进口来源国证据仍需补齐"}];
const coverage=[
  ["KZ","已覆盖","今日覆盖","部分覆盖","待验证","部分覆盖"],
  ["UZ","已覆盖","今日覆盖","部分覆盖","待验证","部分覆盖"],
  ["KG","已覆盖","今日覆盖","部分覆盖","暂无来源","待验证"],
  ["TJ","镜像覆盖","今日覆盖","待验证","暂无来源","待验证"],
  ["TM","镜像覆盖","今日覆盖","待验证","暂无来源","待验证"],
];

export default function CorporateHome(){return <div className="marketing-site decision-home">
  <SiteNav/>
  <main>
    <section className="decision-hero"><div><span>YINHENG · CENTRAL ASIA MARKET ENTRY</span><h1>中亚食用菌出海决策平台</h1><p>整合五国贸易、价格、渠道与物流信息，帮助菌企选择目标市场并验证进入条件。</p><div><a className="corp-primary" href="/data">进入数据中心</a><a className="corp-secondary" href="#markets">查看重点市场 →</a></div></div><Image src="/central-asia-corridor.png" alt="喀什连接中亚的跨境物流与农业走廊" width={1536} height={1024} priority/></section>

    <section className="decision-section"><header><span>THREE DECISIONS</span><h2>进入中亚前，先回答三个问题</h2></header><div className="decision-question-grid">{[["01","哪个国家值得进入","比较市场容量、增长趋势、竞争来源和证据完整度。"],["02","什么产品存在机会","结合贸易品类、零售价格和渠道供给识别验证方向。"],["03","到岸成本和风险如何","核对物流、准入、规格与真实成交条件，不用挂牌价替代成交价。"]].map(x=><article key={x[0]}><span>{x[0]}</span><h3>{x[1]}</h3><p>{x[2]}</p></article>)}</div></section>

    <section className="decision-section decision-capabilities"><header><span>AVAILABLE CAPABILITIES</span><h2>当前可使用的市场进入能力</h2></header><div className="decision-capability-grid">{[["国别市场研究","贸易规模、竞争来源、风险与证据缺口","/insights/country"],["五国价格监测","按国家、品类、规格和平台查看可追溯报价","/terminal"],["商机与风险验证","把市场信号拆成证据、风险和下一步任务","/opportunities"],["定制研究与合作对接","围绕具体产品与国家准备验证方案","/expand/contact"]].map(x=><a href={x[2]} key={x[0]}><h3>{x[0]}</h3><p>{x[1]}</p><b>进入使用 →</b></a>)}</div></section>

    <section className="decision-section" id="markets"><header><span>FOCUS MARKETS</span><h2>优先看懂两个重点市场</h2><p>结论来自现有 2024 年贸易口径与已核验价格观察；缺失维度明确标注，不作确定性推断。</p></header><div className="focus-market-grid">{focusMarkets.map(item=>{const data=market(item.code);return <article key={item.code}><div className="focus-market-title"><span>{item.code}</span><h3>{item.name}</h3><em>{data.rows[0]?.confidence??"—"} 级证据</em></div><strong>{item.conclusion}</strong><dl><div><dt>已确认贸易规模</dt><dd>{money(data.total)}</dd></div><div><dt>中国金额占比</dt><dd>{data.chinaShare==null?"—":`${data.chinaShare.toFixed(1)}%`}</dd></div><div><dt>重点品类</dt><dd>{data.opportunity?.product??"—"}</dd></div></dl><p><b>主要风险：</b>{item.risk}</p><p><b>下一步：</b>{data.opportunity?.nextAction??"补充渠道与价格证据"}</p><small>口径：UN Comtrade 2024 进口申报；HS 070951/200310；更新时间 2026-08-17。</small><a href={`/countries/${item.code.toLowerCase()}`}>查看完整市场判断 →</a></article>})}</div></section>

    <section className="decision-section coverage-matrix-section"><header><span>FIVE-COUNTRY COVERAGE</span><h2>五国证据覆盖矩阵</h2><p>“已覆盖”不等于结论成熟；渠道、物流和准入仍需结合真实业务持续验证。</p></header><div className="coverage-matrix"><div className="coverage-matrix-row head"><b>国家</b><span>贸易</span><span>价格</span><span>渠道</span><span>物流</span><span>准入</span></div>{coverage.map(row=><div className="coverage-matrix-row" key={row[0]}>{row.map((cell,i)=>i===0?<b key={cell}>{countryOptions.find(x=>x.code===cell)?.label}</b>:<span className={cell==="已覆盖"||cell==="今日覆盖"?"covered":cell==="暂无来源"?"missing":"partial"} key={`${row[0]}-${i}`}>{cell}</span>)}</div>)}</div><small>状态更新时间：2026-08-17；贸易来源为 UN Comtrade 及伙伴国镜像，价格为公开市场挂牌观察。</small></section>

    <section className="decision-action"><div><span>NEXT STEP</span><h2>从目标市场开始验证</h2><p>先看国别判断和底层证据，再提交产品、产能与目标国家，形成下一步验证清单。</p></div><div><a href="/countries/kz">获取哈萨克斯坦样例</a><a href="/expand/contact">提交目标市场</a><a href="/opportunities">申请市场验证</a></div></section>
  </main>
  <MarketingFooter/>
</div>}
