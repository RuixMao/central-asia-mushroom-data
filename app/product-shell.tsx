import Link from "next/link";

export default function ProductShell({ children }: { children: React.ReactNode }) {
  return <div className="saas-site"><header className="saas-nav"><Link href="/" className="saas-logo"><span>枢</span><b>中亚菌业数据终端</b></Link><nav><Link href="/catalog">数据目录</Link><Link href="/reports">AI 报告</Link><Link href="/docs">API</Link><Link href="/pricing">定价</Link></nav><Link className="saas-account" href="/dashboard">账户后台</Link></header>{children}<footer className="saas-footer"><div><b>因恒科技</b><span>让中亚菌类贸易决策有据可查</span></div><nav><Link href="/catalog">数据目录</Link><Link href="/docs">API 文档</Link><Link href="/privacy">隐私政策</Link><Link href="/terms">使用条款</Link></nav></footer></div>;
}
