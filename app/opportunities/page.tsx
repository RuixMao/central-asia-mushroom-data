import ProductShell from "../product-shell";
import { OpportunityRadar } from "../theme-live-data";

export const metadata={title:"商机雷达｜中亚食用菌出海服务平台"};

export default function OpportunitiesPage(){return <ProductShell><main className="saas-main">
  <section className="saas-hero compact"><span>MARKET OPPORTUNITIES</span><h1>从数据变化中，发现值得验证的商业机会</h1><p>机会分用于安排研究和业务验证顺序，不代表成交预测。每条信号均保留证据等级、覆盖度和下一步动作。</p></section>
  <OpportunityRadar/>
  <section className="page-cta radar-cta"><div><span>NEXT STEP</span><h2>把信号转成目标市场验证任务</h2><p>查看底层价格与贸易来源，或提交产品、目标国家和合作需求。</p></div><div><a href="/terminal">核验底层数据 →</a><a href="/expand/contact">提交合作需求 →</a></div></section>
</main></ProductShell>}
