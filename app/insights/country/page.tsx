import ProductShell from "../../product-shell";
import CountryAccordion from "./country-accordion";
export const metadata={title:"国家市场｜食用菌出海市场决策平台"};
export default function Page(){return <ProductShell><main className="saas-main"><section className="saas-hero compact"><span>国家市场</span><h1>比较目标市场</h1><p>价格、贸易、渠道、物流与准入信息。</p><div className="market-anchor-nav"><a href="/opportunities" data-native-navigation="true">查看市场机会</a><a href="/market" data-native-navigation="true">查看价格行情</a></div></section><CountryAccordion/></main></ProductShell>}
