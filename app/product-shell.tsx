import Link from "next/link";
import Image from "next/image";

const primary=[["/","首页"],["/market-data","数据中心"],["/terminal","数据终端"],["/catalog","数据目录"],["/reports","市场报告"],["/mushroom","菌类出海"],["/docs","API"],["/pricing","定价"]];

export function GlobalHeader(){return <header className="saas-nav global-nav"><Link href="/" className="saas-logo global-logo" aria-label="因恒科技首页"><Image src="/inhen-tech-logo.png" alt="因恒科技 Inhen Tech" width={282} height={90} priority /></Link><nav aria-label="全站导航">{primary.map(([href,label])=><Link href={href} key={href}>{label}</Link>)}<details><summary>更多</summary><div><Link href="/solutions/trade">解决方案</Link><Link href="/services">数据服务</Link><Link href="/opportunities">市场商机</Link><Link href="/data-assets">数据资产</Link></div></details></nav><Link className="saas-account" href="/dashboard">账户后台</Link></header>}
export function GlobalFooter(){return <footer className="saas-footer global-footer"><div><b>因恒科技 · 中亚菌类数据平台</b><span>让中亚菌类贸易与零售价格决策有据可查</span></div><nav><Link href="/market-data">数据中心</Link><Link href="/terminal">数据终端</Link><Link href="/catalog">数据目录</Link><Link href="/docs">API 文档</Link><Link href="/privacy">隐私政策</Link><Link href="/terms">使用条款</Link></nav></footer>}
export default function ProductShell({children,className=""}:{children:React.ReactNode;className?:string}){return <div className={`saas-site ${className}`.trim()}><GlobalHeader/>{children}<GlobalFooter/></div>}
