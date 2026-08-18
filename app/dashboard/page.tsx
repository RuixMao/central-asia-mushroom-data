import ProductShell from "../product-shell";

const services = [
  { tag: "MARKET DATA", title: "市场数据服务", copy: "获取中亚五国食用菌价格、贸易规模、品类结构与来源口径。", href: "/data", cta: "查看数据中心" },
  { tag: "MARKET RESEARCH", title: "专项市场研究", copy: "围绕目标国家、产品规格、渠道、物流与准入条件形成研究交付。", href: "/pricing", cta: "查看服务方式" },
  { tag: "COOPERATION", title: "合作需求对接", copy: "提交产品、产能、目标国家与合作方向，由商务团队进一步沟通。", href: "/expand/contact", cta: "提交合作需求" },
];

export default function CustomerServicePage(){return <ProductShell><main className="saas-main dashboard-page">
  <section className="dashboard-title"><div><span>CLIENT SERVICES</span><h1>客户服务</h1><p>选择数据、研究或合作服务，获取与您目标市场相匹配的支持。</p></div><a href="/expand/contact">联系商务团队</a></section>
  <section className="dashboard-grid customer-service-grid">{services.map(item=><article key={item.title}><div><span>{item.tag}</span><h2>{item.title}</h2></div><p>{item.copy}</p><a href={item.href}>{item.cta} →</a></article>)}</section>
  <section className="page-cta"><div><span>SERVICE REQUEST</span><h2>已有明确国家与产品？</h2><p>提交规格、产能和目标市场，我们将据此确认可提供的数据与研究范围。</p></div><a href="/expand/contact">提交具体需求 →</a></section>
</main></ProductShell>}
