import ProductShell from "../../product-shell";
const modes=["出口意向","境外园区","菌包产能","智慧方舱"];
export default function Page(){return <ProductShell><main className="saas-main"><section className="saas-hero compact"><span>EXPANSION CASES</span><h1>中国企业中亚拓展图谱</h1><p>企业名称、地点、事实和日期必须具有可核验来源；当前未达到公开发布标准的案例不展示。</p></section><section className="detail-card-grid">{modes.map(x=><article key={x}><span>{x}</span><h2>案例收集中</h2><p>取得企业公开公告、政府项目文件或权威媒体原文后更新。</p></article>)}</section></main></ProductShell>}
