import ProductShell from "../product-shell";
import { OpportunityRadar } from "../theme-live-data";

export const metadata={title:"商机雷达｜中亚食用菌出海服务平台"};

export default function OpportunitiesPage(){return <ProductShell><main className="saas-main">
  <section className="saas-hero compact"><span>MARKET OPPORTUNITIES</span><h1>从数据变化中，发现值得验证的商业机会</h1><p>机会信号用于比较市场关注度，不代表成交预测；每条信息均保留证据等级、覆盖度与关键验证条件。</p></section>
  <OpportunityRadar/>
  <section className="page-cta radar-cta"><div><span>MARKET VALIDATION</span><h2>进一步验证目标市场</h2><p>查看价格与贸易依据，或提交产品、目标国家和合作需求。</p></div><div><a href="/terminal">查看数据依据 →</a><a href="/expand/contact">提交合作需求 →</a></div></section>
</main></ProductShell>}
