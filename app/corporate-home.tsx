import Image from "next/image";
import Link from "next/link";
import SiteNav from "./site-nav";
import MarketingFooter from "./marketing-footer";
import { countryOptions } from "./data";
import {HomeMarketCards,HomePriceOverview} from "./home-live-markets";
const coverage=[
  ["KZ","已覆盖","今日覆盖","部分覆盖","3条参考价","部分覆盖"],
  ["UZ","已覆盖","今日覆盖","部分覆盖","待验证","部分覆盖"],
  ["KG","已覆盖","今日覆盖","部分覆盖","暂无来源","待验证"],
  ["TJ","镜像覆盖","今日覆盖","待验证","暂无来源","待验证"],
  ["TM","镜像覆盖","今日覆盖","待验证","暂无来源","待验证"],
  ["LA","公开信息","已有报价","零售渠道","已有线路","按产品咨询"],
  ["VN","公开信息","已有报价","零售渠道","已有线路","按产品咨询"],
  ["TH","公开信息","已有报价","零售渠道","已有线路","按产品咨询"],
  ["MM","公开信息","已有报价","零售渠道","已有线路","按产品咨询"],
  ["KH","公开信息","已有报价","零售渠道","已有线路","按产品咨询"],
];

export default function CorporateHome(){return <div className="marketing-site decision-home">
  <SiteNav/>
  <main>
    <section className="decision-hero"><div><span>食用菌国际市场判断与落地验证</span><h1>让食用菌出海决策有数据可依</h1><p>比较目标市场的贸易规模、当地价格、渠道、物流和进入风险，再决定是否报价、打样或试单。</p><div><Link className="corp-primary" href="/insights/country">帮我选择目标市场</Link><Link className="corp-secondary" href="/market">查询当地价格 →</Link></div><small className="hero-trust-note">价格、贸易和渠道信息均标明更新时间，便于快速比较。</small></div><Image src="/central-asia-corridor.png" alt="连接中国与目标市场的跨境贸易走廊" width={1536} height={1024} priority/></section>

    <HomePriceOverview/>

    <section className="decision-section"><header><span>从您的问题开始</span><h2>现在最想解决哪一步？</h2></header><div className="decision-question-grid">{[["01","不知道先做哪个国家","比较市场规模、竞争、渠道和风险，缩小目标范围。","/insights/country","比较目标市场"],["02","不知道当地能卖多少钱","按国家、菌种、规格和渠道查看公开价格，判断报价空间。","/market","查询当地价格"],["03","担心机会无法真正落地","核对物流、准入、渠道和证据缺口，明确试单前还要验证什么。","/opportunities","查看待验证机会"]].map(x=><article key={x[0]}><span>{x[0]}</span><h3>{x[1]}</h3><p>{x[2]}</p><Link href={x[3]}>{x[4]} →</Link></article>)}</div></section>

    <section className="decision-section decision-capabilities"><header><span>您的下一步</span><h2>从初步判断走到实际行动</h2></header><div className="decision-capability-grid">{[["选择目标国家","先比较市场规模、竞争来源和进入风险","/insights/country","看看哪个国家更适合"],["判断价格空间","比较同类产品在不同城市和渠道的公开价格","/market","查询我的品类"],["核实关键风险","明确物流、准入和渠道成交还缺哪些证据","/opportunities","查看验证清单"],["获得针对性建议","围绕您的产品、产能和目标国家制定验证方案","/expand/contact","提交我的具体情况"]].map(x=><Link href={x[2]} key={x[0]}><h3>{x[0]}</h3><p>{x[1]}</p><b>{x[3]} →</b></Link>)}</div></section>

    <section className="decision-section" id="markets"><header><span>市场比较</span><h2>值得关注的市场机会</h2><p>直接查看已经形成的价格、渠道和品种数字。</p></header><HomeMarketCards/></section>

    <section className="decision-section coverage-matrix-section"><header><span>市场覆盖</span><h2>中亚与东南亚市场信息</h2><p>查看各国的贸易、价格、渠道、物流与进入服务。</p></header><div className="coverage-matrix"><div className="coverage-matrix-row head"><b>国家</b><span>市场规模</span><span>公开价格</span><span>销售渠道</span><span>物流成本</span><span>进入要求</span></div>{coverage.map(row=><div className="coverage-matrix-row" key={row[0]}>{row.map((cell,i)=>i===0?<b key={cell}>{countryOptions.find(x=>x.code===cell)?.label}</b>:<span className={cell==="已覆盖"||cell==="今日覆盖"||cell==="已有报价"?"covered":cell==="暂无来源"?"missing":"partial"} key={`${row[0]}-${i}`}>{cell==="镜像覆盖"?"伙伴国贸易记录":cell==="今日覆盖"?"已有公开价格":cell==="暂无来源"?"欢迎咨询":cell==="待验证"?"按产品咨询":cell}</span>)}</div>)}</div><small>公开价格不等于真实成交价，物流与准入请按具体产品咨询。</small></section>

    <section className="decision-action"><div><span>不知道下一步怎么选？</span><h2>告诉我们您的产品和目标，我们帮您整理验证清单</h2><p>您将知道应该先核实哪个国家、价格、渠道和风险，不必从大量数据中自己找答案。</p></div><div><Link href="/expand/contact">提交我的具体情况</Link><Link href="/insights/country">先比较目标市场</Link></div></section>
  </main>
  <MarketingFooter/>
</div>}
