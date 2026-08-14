"use client";
import { FormEvent, useEffect, useState } from "react";
import Image from "next/image";

const products=[
  ["市场", "中亚市场信息", "持续汇集区域宏观、贸易、价格与政策信息，形成清晰的市场脉络。"],
  ["宏观", "宏观经济数据库", "围绕中亚五国建立可追溯的经济、贸易与产业数据框架。"],
  ["产业", "行业与产业研究", "聚焦农业及关联产业，识别供需结构、产业链变化与区域机会。"],
  ["企业", "企业信息服务", "逐步建设进口商、经销商、园区及项目主体的结构化资料。"],
  ["监测", "风险与机会监测", "通过多源核验发现数据异常、市场变化与优先研究方向。"],
  ["咨询", "定制研究与咨询", "为特定国家、行业与投资议题提供数据梳理和专项研究。"],
];
const solutions=[
  ["financial", "金融机构", "建立区域研究底座，支持国别、行业与项目的前期判断。"],
  ["investors", "跨境投资者", "发现市场结构变化，验证投资假设并识别潜在风险。"],
  ["trade", "国际贸易企业", "研究目标市场、渠道、价格与合作伙伴，提高进入效率。"],
  ["government", "政府及研究机构", "获得口径清晰、来源可追溯的区域数据与专题研究。"],
  ["professional", "专业服务机构", "为咨询、法律、审计和产业服务提供区域事实基础。"],
  ["academic", "高校与学术研究", "支持课题研究、论文数据、区域比较与产学研合作。"],
];
const insights=[
  ["市场观察", "中亚重点菌类贸易结构：增长与口径差异", "梳理五国进口基线，并说明镜像差异如何用于发现转口和统计口径问题。", "2026.08.10", "insight-a", "/central-asia-market.png"],
  ["区域研究", "从喀什看中国—中亚农业数据走廊", "讨论在地资源、公开统计和合作方信息如何形成可持续的数据基础。", "2026.08.10", "insight-b", "/central-asia-corridor.png"],
  ["方法论", "从零散市场信息到可信市场判断", "介绍来源分级、字段标准化、交叉核验和持续更新的研究流程。", "2026.08.10", "insight-c", "/central-asia-research.png"],
];

export default function CorporateHome(){
  const [menu,setMenu]=useState(false); const [sent,setSent]=useState(false); const [lang,setLang]=useState("中文"); const [role,setRole]=useState("产能方");
  useEffect(()=>{setRole(localStorage.getItem("yinheng-role")||"产能方")},[]);
  const chooseRole=(next:string)=>{setRole(next);localStorage.setItem("yinheng-role",next)};
  const submit=(e:FormEvent)=>{e.preventDefault();setSent(true)};
  return <div className="corp-site">
    <header className="corp-nav"><a className="corp-logo" href="#home" aria-label="因恒科技首页"><Image src="/inhen-tech-logo.png" alt="因恒科技 Inhen Tech" width={282} height={90} priority /></a><button className="menu-toggle" aria-label="打开导航" aria-expanded={menu} onClick={()=>setMenu(!menu)}>☰</button><nav className={menu?"open":""}>{[["#home","首页"],["/market","市场行情"],["/insights","需求分析"],["/expand","出海路径"],["/terminal","数据产品"],["/solutions/trade","解决方案"],["/pricing","定价"]].map(([href,label])=><a href={href} key={href} onClick={()=>setMenu(false)}>{label}</a>)}</nav><button className="lang-switch" onClick={()=>setLang(lang==="中文"?"EN":"中文")} aria-label="切换语言">{lang}⌄</button><a className="nav-demo" href="#contact">合作对接</a></header>
    <main>
      <section className="corp-hero" id="home"><div className="corp-hero-copy"><span>YINHENG · MUSHROOM GOING GLOBAL</span><h1>中亚食用菌出海<br/>从行情研判到合作对接</h1><p>以中亚五国贸易、价格、渠道和市场研究为基础，为产能方、渠道商、投资者与研究者提供数据驱动的商业分析和出海服务。</p><div><a className="corp-primary" href="/market">查看市场行情</a><a className="corp-secondary" href="/expand/contact">发起合作对接 →</a></div></div><div className="corp-hero-visual"><Image src="/central-asia-corridor.png" alt="喀什连接中亚的跨境物流与农业走廊" width={1536} height={1024} priority/><div className="visual-caption"><span>REGIONAL FOCUS</span><b>中国 · 喀什 · 中亚五国</b></div></div></section>

      <section className="home-use-section"><div className="corp-section-head"><span>DECISION PATH</span><h2>看行情、挖需求、找路径</h2></div><div className="home-use-grid">{[["市场行情","看五国现在什么价、有哪些新品类","/market"],["需求分析","比较贸易、渠道与供应结构","/insights"],["出海路径","查看菌情、商机与合作入口","/expand"]].map(([title,copy,href])=><a href={href} key={href}><span>OPEN</span><h3>{title}</h3><p>{copy}</p><b>进入使用 →</b></a>)}</div></section>

      <section className="role-section"><div><span>YOUR ROLE</span><h2>选择您的角色</h2><p>{role==="产能方"?"推荐：查看目标国价格、渠道和出口机会。":role==="渠道商"?"推荐：跟踪品类供应、价格区间与市场报告。":role==="投资者"?"推荐：从五国贸易规模、政策和可信度开始。":"推荐：进入数据目录、方法说明与报告中心。"}</p></div><div>{["产能方","渠道商","投资者","研究者"].map(item=><button className={role===item?"active":""} onClick={()=>chooseRole(item)} key={item}>{item}</button>)}</div></section>

      <section className="value-section"><div className="corp-section-head"><span>CORE VALUE</span><h2>从分散信息到可执行判断</h2><p>以区域专注、多源整合和严谨研究，降低中亚市场的信息获取与验证成本。</p></div><div className="value-grid">{[["整","区域数据整合","统一整理宏观、贸易、产业和市场信息，保留来源与统计口径。"],["监","市场持续监测","跟踪价格、渠道、政策和项目变化，形成连续的市场观察。"],["研","企业与产业研究","围绕重点行业、企业和产业链建立结构化研究框架。"],["策","决策研究服务","将数据转化为简报、专题报告和可执行的研究建议。"]].map(([icon,title,copy])=><article key={title}><i>{icon}</i><h3>{title}</h3><p>{copy}</p><a href="#products">了解更多 →</a></article>)}</div></section>

      <section className="home-data-section"><div className="home-data-intro"><span>MARKET DATA SAMPLE · 2024</span><h2>用一组数据，看见区域市场结构</h2><p>以下为现有菌类贸易基线的公开数据样例。首页只呈现决策摘要，完整记录、口径说明与来源可进入数据中心查看。</p><a href="/market-data">进入数据中心 →</a></div><div className="home-data-panel"><div className="home-data-kpis"><div><strong>$6.96M</strong><span>已报告重点菌类进口额</span></div><div><strong>9</strong><span>2022–2024 贸易记录组</span></div><div><strong>5</strong><span>中亚国家覆盖</span></div><div><strong>5类</strong><span>可追溯来源类型</span></div></div><div className="home-market-list"><div><span>01</span><b>哈萨克斯坦</b><i style={{width:"100%"}}></i><strong>$5.63M</strong></div><div><span>02</span><b>吉尔吉斯斯坦</b><i style={{width:"14.3%"}}></i><strong>$805K</strong></div><div><span>03</span><b>乌兹别克斯坦</b><i style={{width:"9.3%"}}></i><strong>$525K</strong></div></div><small>口径：HS 070951、070959、200310；缺失值不按 0 处理。来源：UN Comtrade 基线整理。</small></div></section>

      <section className="product-section" id="products"><div className="corp-section-head"><span>PRODUCTS & SERVICES</span><h2>服务中亚研究与跨境决策</h2><p>当前阶段以数据整合、区域研究和定制服务为核心，专业数据终端将在后续独立推出。</p></div><div className="corp-product-grid">{products.map(([tag,title,copy],i)=><article key={title}><span>0{i+1} / {tag}</span><h3>{title}</h3><p>{copy}</p><a href="#contact">咨询产品 →</a></article>)}</div></section>

      <section className="coverage-section" id="coverage"><div className="coverage-copy"><span>REGIONAL DATA NETWORK</span><h2>喀什—中亚五国<br/>数据覆盖网络</h2><p>以喀什为跨境数据服务枢纽，持续汇集贸易、价格、渠道与投资机会信息；每条数据均标注来源、更新时间与验证状态。</p><div className="coverage-stats"><div><strong>5</strong><span>中亚国家持续覆盖</span></div><div><strong>4类</strong><span>核心数据来源</span></div><div><strong>3年</strong><span>已验证贸易基线</span></div><div><strong>多频</strong><span>月 / 季 / 年更新</span></div></div></div><div className="coverage-visual"><div className="coverage-map" aria-label="喀什连接中亚五国的数据覆盖网络"><div className="map-orbit orbit-a"></div><div className="map-orbit orbit-b"></div>{[1,2,3,4,5].map(i=><i className={`map-route route-${i}`} key={i}></i>)}<div className="map-hub"><span>跨境数据服务枢纽</span><strong>喀什</strong><small>数据汇集 · 市场分析 · 渠道连接</small></div>{[
        {code:"KZ",name:"哈萨克斯坦",metric:"2024 重点菌类 $5.63M",status:"实时接口",tone:"live"},
        {code:"UZ",name:"乌兹别克斯坦",metric:"贸易与市场基线",status:"官方最新",tone:"official"},
        {code:"KG",name:"吉尔吉斯斯坦",metric:"贸易与渠道监测",status:"验证基线",tone:"baseline"},
        {code:"TJ",name:"塔吉克斯坦",metric:"贸易与机会跟踪",status:"验证基线",tone:"baseline"},
        {code:"TM",name:"土库曼斯坦",metric:"公开资料监测",status:"",tone:""}
      ].map((market,i)=><article className={`map-market market-${i+1}`} key={market.code}><div><b>{market.code}</b><strong>{market.name}</strong></div><p>{market.metric}</p>{market.status&&<em className={market.tone}>{market.status}</em>}</article>)}</div><div className="coverage-legend"><span><i className="live"></i>实时接口</span><span><i className="official"></i>官方最新</span><span><i className="baseline"></i>已验证基线</span></div><p className="coverage-note">连线表示数据与业务覆盖关系，不代表地理距离、贸易规模或国家排名。</p></div></section>

      <section className="solution-section" id="solutions"><div className="corp-section-head"><span>SOLUTIONS</span><h2>面向不同机构的区域研究支持</h2></div><div className="solution-list">{solutions.map(([slug,title,copy],i)=><article key={slug}><span>0{i+1}</span><h3>{title}</h3><p>{copy}</p><a href={`/solutions/${slug}`}>了解方案 →</a></article>)}</div></section>

      <section className="insight-section" id="insights"><div className="corp-section-head"><span>MARKET INSIGHTS</span><h2>研究、观点与方法</h2><p>以少而精的专题内容，展示对中亚市场的持续观察和研究能力。</p></div><div className="insight-grid">{insights.map(([cat,title,copy,date,cls,image])=><article key={title}><div className={`insight-cover ${cls}`}><Image src={image} alt="" fill sizes="(max-width: 580px) 100vw, (max-width: 820px) 50vw, 33vw"/><span>{cat}</span><b>YINHENG<br/>RESEARCH</b></div><div className="insight-body"><span>{cat} · {date}</span><h3>{title}</h3><p>{copy}</p><a href="#contact">获取样例报告 →</a></div></article>)}</div></section>

      <section className="trust-section" id="about"><div className="corp-section-head"><span>TRUST & METHODOLOGY</span><h2>可信度来自清晰的方法，而不是夸大的数字</h2></div><div className="trust-process">{[["01","来源分级","区分官方统计、行业资料、市场观察与合作方信息。"],["02","字段标准化","统一国家、商品、时间、币种、单位与主体标识。"],["03","交叉核验","通过报告国与伙伴国、公开信息与市场观察相互验证。"],["04","持续更新","保留采集时间、更新频率、缺失值与置信等级。"]].map(([no,title,copy])=><article key={no}><span>{no}</span><h3>{title}</h3><p>{copy}</p></article>)}</div><div className="source-line"><span>当前基础来源类型</span><b>联合国贸易统计</b><b>中国海关口径</b><b>FAOSTAT</b><b>市场公开挂牌</b><b>行业资料</b></div></section>

      <section className="contact-section" id="contact"><div className="contact-copy"><span>GET IN TOUCH</span><h2>开始了解中亚市场</h2><p>联系我们，获取产品介绍、样例报告或定制化解决方案。提交后，我们将根据您的机构类型和研究议题进一步沟通。</p><div><b>适用机构</b><span>金融机构 · 投资者 · 跨境企业 · 研究机构 · 专业服务机构</span></div></div><form onSubmit={submit}>{sent?<div className="form-success"><b>需求已记录</b><p>感谢您的关注。当前为网站演示版本，正式联系方式接入后可完成提交与跟进。</p><button type="button" onClick={()=>setSent(false)}>返回表单</button></div>:<><label>姓名<input required name="name" placeholder="请输入姓名"/></label><label>机构<input required name="company" placeholder="请输入机构名称"/></label><label>联系邮箱<input required type="email" name="email" placeholder="name@company.com"/></label><label>需求类型<select name="need" defaultValue="demo"><option value="demo">申请产品演示</option><option value="report">获取样例报告</option><option value="research">定制研究与咨询</option><option value="cooperation">商务合作</option></select></label><label className="full">关注的问题<textarea name="message" placeholder="请简要说明关注的国家、行业或研究议题"/></label><button className="form-submit" type="submit">提交需求 →</button></>}</form></section>
    </main>
    <footer className="corp-footer"><div className="footer-brand"><Image className="footer-logo-image" src="/inhen-tech-logo.png" alt="因恒科技 Inhen Tech" width={282} height={90} /><p>面向国际投资者、金融机构、企业管理者和研究人员的中亚数据与市场研究平台。</p></div><div><b>产品</b><a href="#products">市场信息</a><a href="/market-data">区域数据中心</a><a href="#products">研究与咨询</a></div><div><b>解决方案</b><a href="#solutions">金融机构</a><a href="#solutions">跨境投资者</a><a href="#solutions">国际贸易企业</a></div><div><b>联系</b><a href="#contact">申请演示</a><a href="#contact">联系我们</a><a href="#insights">市场洞察</a></div><div><b>法律</b><a href="/privacy">隐私政策</a><a href="/terms">使用条款</a><span>数据终端 · 即将推出</span></div><div className="footer-bottom"><span>© 2026 因恒科技</span><span>公开信息仅供研究参考，不构成投资或交易建议。</span></div></footer>
  </div>
}
