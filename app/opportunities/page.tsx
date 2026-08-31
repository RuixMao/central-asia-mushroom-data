import ProductShell from "../product-shell";
import { OpportunityRadar } from "../theme-live-data";

export const metadata={title:"市场机会｜食用菌出海市场决策平台"};

export default function OpportunitiesPage(){return <ProductShell><main className="saas-main">
  <section className="saas-hero compact"><span>市场机会</span><h1>哪些国家和品种值得关注？</h1><p>查看价格、贸易、渠道机会与主要风险。</p></section>
  <OpportunityRadar/>
  <section className="page-cta radar-cta"><div><span>研究咨询</span><h2>定制目标市场研究</h2><p>覆盖贸易、价格、物流、准入与渠道。</p></div><div><a href="/market">查看价格行情 →</a><a href="/expand/contact">提交研究需求 →</a></div></section>
</main></ProductShell>}
