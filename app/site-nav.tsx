const links = [
  ["/", "首页"],
  ["/terminal", "数据终端"],
  ["/catalog", "数据目录"],
  ["/reports", "AI 报告"],
  ["/pricing", "订阅方案"],
];

export default function SiteNav() {
  return (
    <header className="site-nav">
      <Link className="site-logo" href="/"><span>枢</span><strong>因恒科技</strong><small>CENTRAL ASIA DATA</small></Link>
      <nav aria-label="网站导航">{links.map(([href, label]) => <a key={href} href={href}>{label}</a>)}</nav>
      <a className="site-nav-cta" href="/dashboard">账户后台</a>
    </header>
  );
}
import Link from "next/link";
