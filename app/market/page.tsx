import ProductShell from "../product-shell";
import { MarketLivePreview } from "../theme-live-data";
export const metadata={title:"市场行情｜中亚食用菌出海服务平台"};
export default function Page(){return <ProductShell><main className="saas-main"><section className="saas-hero compact"><span>MARKET CONDITIONS</span><h1>中亚食用菌市场行情</h1><p>从国家、城市、渠道和品类查看公开挂牌价，并保持汇率、规格和日期透明。</p></section><MarketLivePreview/><section className="detail-card-grid"><article><span>基础行情</span><h2>五国品类价格</h2><p>查看当地货币价格、人民币参考价、规格与来源。</p><a href="/market/prices">进入价格行情 →</a></article><article><span>新品扫描</span><h2>更多菌类与产品形态</h2><p>追踪香菇、平菇、金针菇等已出现的市场记录。</p><a href="/market/scan">进入品类扫描 →</a></article><article><span>实时大屏</span><h2>贸易与价格总览</h2><p>适合会议室和展厅投屏的五国数据视图。</p><a href="/screen">打开大屏 →</a></article></section></main></ProductShell>}
