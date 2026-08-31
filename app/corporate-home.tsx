import Image from "next/image";
import Link from "./native-link";
import SiteNav from "./site-nav";
import MarketingFooter from "./marketing-footer";
import {HomeMarketMatrix,HomePriceOverview,HomeSignalOverview} from "./home-live-markets";

export default function CorporateHome(){return <div className="marketing-site decision-home">
  <SiteNav/>
  <main>
    <section className="decision-hero"><div><span>因恒科技市场情报</span><h1>食用菌跨境市场数据与研究咨询</h1><p>持续跟踪中亚、东南亚及新增目标市场的海关贸易、电商零售、渠道与物流数据。</p><div><Link className="corp-primary" href="/market">查看市场数据</Link><Link className="corp-secondary" href="/expand/contact">提交需求 →</Link></div></div><Image src="/central-asia-corridor.png" alt="连接中国与海外市场的跨境贸易走廊" width={1536} height={1024} priority/></section>

    <HomePriceOverview/>

    <section className="decision-section"><header><span>平台能力</span><h2>从市场数据到专项研究</h2></header><div className="decision-capability-grid">{[["海关贸易数据库","按国家、伙伴国、HS 编码和年度查询进出口规模与结构。","/insights/trade","查看贸易数据"],["电商零售监测","跟踪商品名称、规格、原币价格、标准化价格、渠道与采集日期。","/market","查看价格行情"],["市场与渠道研究","整合国别市场、销售渠道、物流路线、准入条件与商业机会。","/opportunities","比较目标市场"],["定制研究咨询","围绕产品、目标国家和业务问题提供专题数据与研究交付。","/expand/contact","提交需求"]].map(([title,copy,href,cta],index)=><Link href={href} key={title}><span>{String(index+1).padStart(2,"0")}</span><h3>{title}</h3><p>{copy}</p><b>{cta} →</b></Link>)}</div></section>

    <section className="decision-section"><header><span>快速入口</span><h2>您现在要做什么？</h2></header><div className="decision-question-grid">{[["01","选市场","比较重点市场的价格、渠道与贸易数据。","/opportunities","比较市场"],["02","查价格","按国家、品种和渠道查看报价。","/market","查询价格"],["03","定制研究","提交研究主题、产品与目标市场。","/expand/contact","提交需求"]].map(x=><article key={x[0]}><span>{x[0]}</span><h3>{x[1]}</h3><p>{x[2]}</p><Link href={x[3]}>{x[4]} →</Link></article>)}</div></section>

    <HomeSignalOverview/>
    <HomeMarketMatrix/>

    <section className="decision-action"><div><span>研究咨询</span><h2>需要进一步的市场研究？</h2><p>提交研究主题、产品与目标市场。</p></div><div><Link href="/expand/contact">提交需求</Link></div></section>
  </main>
  <MarketingFooter/>
</div>}
