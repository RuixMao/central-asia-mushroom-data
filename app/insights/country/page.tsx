import ProductShell from "../../product-shell";
import CountryAccordion from "./country-accordion";
export default function Page(){return <ProductShell><main className="saas-main"><section className="saas-hero compact"><span>目标市场</span><h1>目标市场需求画像</h1><p>点击国家即可查看贸易额、主力品种价格、渠道数和更新时间。</p><div className="market-anchor-nav"><a href="/market/prices" data-native-navigation="true">按国家筛选全部价格</a><a href="/market-data" data-native-navigation="true">查看全部市场数据</a></div></section><CountryAccordion/></main></ProductShell>}
