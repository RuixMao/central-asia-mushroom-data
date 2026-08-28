import ProductShell from "../../product-shell"; import PriceLiveTable from "../price-live-table";
export default function Page(){return <ProductShell><main className="saas-main"><section className="saas-hero compact"><span>PRICE DATA</span><h1>食用菌出海价格数据</h1><p>查看按公斤标准化的公开挂牌价，并在中亚与东南亚目标市场间比较。</p></section><section className="subpage-panel"><PriceLiveTable/></section></main></ProductShell>}
