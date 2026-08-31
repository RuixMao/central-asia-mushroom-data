import Image from "next/image";
import Link from "./native-link";

const primary=[["/opportunities","找市场"],["/market","查行情"],["/reports","市场洞察"],["/expand","出海服务"]];

export function GlobalHeader(){return <header className="saas-nav global-nav"><Link href="/" className="saas-logo global-logo" aria-label="因恒科技首页"><Image src="/inhen-tech-logo.png" alt="因恒科技 Inhen Tech" width={282} height={90} priority /></Link><nav aria-label="主要导航">{primary.map(([href,label])=><Link href={href} key={href}>{label}</Link>)}</nav><details className="mobile-task-nav"><summary aria-label="打开导航">浏览市场</summary><div>{primary.map(([href,label])=><Link href={href} key={href}>{label}</Link>)}</div></details><Link className="saas-account" href="/expand/contact">合作咨询</Link></header>}
export function GlobalFooter(){return <footer className="saas-footer global-footer"><div><b>因恒科技 · 食用菌跨境市场数据与研究咨询</b><span>海关贸易、电商零售、渠道与物流数据</span></div><nav><Link href="/opportunities">找市场</Link><Link href="/market">查行情</Link><Link href="/reports">市场洞察</Link><Link href="/expand">出海服务</Link><Link href="/data-assets">数据说明</Link><Link href="/privacy">隐私政策</Link><Link href="/terms">使用条款</Link></nav></footer>}
export default function ProductShell({children,className=""}:{children:React.ReactNode;className?:string}){return <div className={`saas-site ${className}`.trim()}><GlobalHeader/>{children}<GlobalFooter/></div>}
