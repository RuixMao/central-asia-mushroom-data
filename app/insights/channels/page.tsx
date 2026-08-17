import ProductShell from "../../product-shell";

const channels=[
  ["Kaspi","电商平台","哈萨克斯坦","公开商品页"],
  ["O!Market","电商平台","吉尔吉斯斯坦","公开商品页"],
  ["Globus","商超 / 零售","吉尔吉斯斯坦","公开商品页"],
  ["Yandex Uzbekistan","电商平台","乌兹别克斯坦","公开商品页"],
  ["Somon","分类信息","塔吉克斯坦","公开商品页"],
  ["Gipertm","电商平台","土库曼斯坦","公开商品页"],
];

export const metadata={title:"渠道地图｜中亚食用菌出海服务平台"};

export default function Page(){return <ProductShell><main className="saas-main"><section className="saas-hero compact"><span>CHANNEL MAP</span><h1>中亚菌类渠道地图</h1><p>仅列出已纳入公开价格观察的渠道；覆盖品类以实际记录为准。渠道存在不代表已经建立采购或合作关系。</p></section><section className="sample-table"><div className="sample-row head"><span>平台</span><span>渠道类型</span><span>国家</span><span>证据类型</span></div>{channels.map(row=><div className="sample-row" key={row[0]}>{row.map(value=><span key={value}>{value}</span>)}</div>)}</section></main></ProductShell>}
