import ProductShell from "../product-shell";
import { OpportunityRadar } from "../theme-live-data";

export const metadata={title:"商机雷达｜中亚食用菌出海服务平台"};

export default function OpportunitiesPage(){return <ProductShell><main className="saas-main">
  <section className="saas-hero compact"><span>验证市场机会</span><h1>哪些机会值得继续投入时间？</h1><p>先比较市场基础、可用信息和关键风险，再决定是否询价、打样或寻找渠道。这里展示的是待验证方向，不是成交预测。</p></section>
  <OpportunityRadar/>
  <section className="page-cta radar-cta"><div><span>下一步怎么做</span><h2>把市场信号变成您的验证清单</h2><p>结合您的产品、成本和目标国家，明确还需核实的价格、物流、准入和渠道条件。</p></div><div><a href="/terminal">核对价格和市场依据 →</a><a href="/expand/contact">提交我的具体情况 →</a></div></section>
</main></ProductShell>}
