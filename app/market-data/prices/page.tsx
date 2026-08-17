import ProductShell from "../../product-shell"; import PriceLiveTable from "../price-live-table";
export default function Page(){return <ProductShell><main className="saas-main"><section className="saas-hero compact"><span>PRICE DATA</span><h1>中亚食用菌价格数据</h1><p>查看按公斤标准化的公开挂牌价，并按国家和品类比较。</p></section><section className="subpage-panel"><PriceLiveTable/></section></main></ProductShell>}
