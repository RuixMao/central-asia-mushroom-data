import SiteNav from "./site-nav";
import MarketingFooter from "./marketing-footer";

const products = [
  ["01", "中亚农业数据终端", "贸易、产量、价格、渠道与来源的一站式查询和交叉核验。", "/terminal", "DATA TERMINAL"],
  ["02", "企业与数据资产库", "管理现有数据、待采字段、企业资源和可销售的数据产品。", "/data-assets", "DATA ASSETS"],
  ["03", "市场机会平台", "从增长、镜像差异、渠道和供需缺口中发现可验证机会。", "/opportunities", "MARKET OPPORTUNITY"],
  ["04", "数据服务", "数据包、指数、API、定制研究与合作方内容交付。", "/services", "DATA SERVICES"],
];

export default function Home() {
  return <div className="marketing-site">
    <SiteNav />
    <main>
      <section className="landing-hero">
        <div className="landing-copy"><span>YINHENG · CENTRAL ASIA AGRI DATA</span><h1>连接中国与中亚，<br />让农业数据触手可及。</h1><p>以喀什为数据与资源网关，把零散的贸易、价格、企业、物流和项目数据转化为可查询、可验证、可持续更新的商业数据资产。</p><div><a className="primary-link" href="/terminal">进入数据终端 <b>↗</b></a><a className="text-link" href="/data-assets">查看数据资产体系 →</a></div></div>
        <div className="landing-network" aria-label="中国经喀什连接中亚五国"><div className="network-title"><span>DATA CORRIDOR</span><b>数据与资源网络</b></div><div className="network-core"><span>中国供给</span><i>→</i><strong>喀什</strong><i>→</i><span>中亚五国</span></div><div className="network-tags"><b>贸易</b><b>价格</b><b>企业</b><b>物流</b><b>项目</b></div><small>公开数据 + 实地资源 + 持续采集</small></div>
      </section>
      <section className="landing-products"><div className="landing-heading"><span>OUR PRODUCTS</span><h2>为跨境农业业务提供完整的数据产品</h2><p>首页只呈现产品入口；每个产品均进入独立页面。</p></div><div className="landing-product-grid">{products.map(([no,title,copy,href,en]) => <a href={href} key={no}><span>{no}</span><div><b>{title}</b><p>{copy}</p></div><i>{en} ↗</i></a>)}</div></section>
      <section className="landing-proof"><div><span>现有基础</span><strong>5国</strong><p>中亚五国市场框架</p></div><div><span>已整合</span><strong>9组</strong><p>重点菌类贸易记录</p></div><div><span>可核验</span><strong>7条</strong><p>市场价格观察</p></div><div><span>核心能力</span><strong>双口径</strong><p>进口CIF × 出口FOB</p></div></section>
      <section className="differentiation"><div className="landing-heading"><span>WHY YINHENG</span><h2>差异化不在于更多页面，而在于独特的数据形成能力</h2></div><div className="diff-grid"><article><b>01</b><h3>喀什在地资源</h3><p>连接中国供给端与中亚市场，把线下渠道和项目关系变成可维护的数据。</p></article><article><b>02</b><h3>多源交叉核验</h3><p>官方贸易、市场挂牌、行业访谈和合作方回传分层管理，不混写证据。</p></article><article><b>03</b><h3>从信息到资产</h3><p>统一字段、来源、更新时间和置信等级，进一步形成指数、数据包和API。</p></article></div></section>
    </main><MarketingFooter />
  </div>;
}
