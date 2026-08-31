import ProductShell from "../../product-shell";
const modes=["出口意向","境外园区","菌包产能","智慧方舱"];
export default function Page(){return <ProductShell><main className="saas-main"><section className="saas-hero compact"><span>出海案例</span><h1>中国菌企出海拓展图谱</h1><p>呈现中国菌企在中亚与东南亚市场的渠道进入、合作与项目落地案例。</p></section><section className="detail-card-grid">{modes.map(x=><article key={x}><span>{x}</span><h2>案例收集中</h2><p>取得企业公开公告、政府项目文件或权威媒体原文后更新。</p></article>)}</section></main></ProductShell>}
