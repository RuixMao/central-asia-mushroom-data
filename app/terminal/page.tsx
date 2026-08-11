import Link from "next/link";
import Image from "next/image";
export default function TerminalPage(){return <main className="coming-page"><Link className="coming-logo" href="/" aria-label="返回因恒科技首页"><Image src="/inhen-tech-logo.png" alt="因恒科技 Inhen Tech" width={282} height={90} priority /></Link><div><span>INTELLIGENCE TERMINAL</span><h1>专业情报终端<br/>即将推出</h1><p>当前阶段专注建设对外品牌与研究服务入口。终端产品将在数据体系和客户工作流验证完成后独立发布。</p><Link href="/#contact">申请产品演示 →</Link></div></main>}
