import ProductShell from "../../product-shell";
import TradeBrowser from "./trade-browser";
export default function Page(){return <ProductShell><main className="saas-main"><section className="saas-hero compact"><span>TRADE DATA</span><h1>食用菌跨境贸易数据</h1><p>按区域、国家和 HS 编码查询各国最新可得进口数据。</p></section><TradeBrowser/></main></ProductShell>}
