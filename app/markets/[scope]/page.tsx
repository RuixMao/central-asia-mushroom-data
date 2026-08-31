import ProductShell from "../../product-shell";
import MarketDetail from "./market-detail";
export default async function Page({params}:{params:Promise<{scope:string}>}){const code=decodeURIComponent((await params).scope).toUpperCase();return <ProductShell><MarketDetail code={code}/></ProductShell>}
