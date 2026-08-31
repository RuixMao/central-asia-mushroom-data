import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";

const solutions = {
  financial: { label: "金融机构", en: "FINANCIAL INSTITUTIONS", headline: "把跨区域数据转化为授信、研究与项目判断", intro: "为银行、基金、保险与金融服务机构建立来源可追溯的国别、行业和企业研究底座。", needs: ["国别与行业风险监测", "项目及交易对手背景", "贸易结构与异常识别", "区域研究简报"], deliverables: ["目标市场宏观与产业数据库", "行业机会与风险看板", "企业及项目尽调数据包", "月度区域研究简报"] },
  investors: { label: "跨境投资者", en: "CROSS-BORDER INVESTORS", headline: "用数据验证投资假设，提前识别市场与执行风险", intro: "围绕市场规模、供需结构、政策、项目和合作方，支持从机会筛选到投资决策。", needs: ["市场进入与规模判断", "竞争与供给结构", "项目可行性验证", "合作方风险识别"], deliverables: ["投资机会雷达", "国别与行业专题研究", "项目比较与评分模型", "合作方背景档案"] },
  trade: { label: "国际贸易企业", en: "菌业国际贸易", headline: "找到市场、渠道、价格与买家，降低菌业出海进入成本", intro: "服务出口商、设备商和跨境供应链企业，连接贸易数据、渠道价格与企业线索。", needs: ["目标国家与品类选择", "进口商和经销商发现", "价格与渠道监测", "物流与到岸成本"], deliverables: ["买家与渠道数据库", "贸易及价格看板", "冷链成本计算模型", "重点客户开发清单"] },
  government: { label: "政府及研究机构", en: "PUBLIC SECTOR & RESEARCH", headline: "建立口径一致、可持续更新的区域研究基础设施", intro: "为政府部门、园区、智库和公共研究机构提供国别数据、产业监测和专题研究。", needs: ["区域经济与产业观察", "招商项目与企业线索", "政策及合作动态", "跨境产业比较"], deliverables: ["区域数据专题库", "招商与项目雷达", "季度产业运行报告", "定制区域研究"] },
  professional: { label: "专业服务机构", en: "专业市场服务", headline: "为咨询、法律、审计与产业服务补齐菌业出海事实底座", intro: "以结构化数据和可追溯证据，提升客户项目的研究效率与交付质量。", needs: ["快速行业扫描", "企业与项目事实核验", "市场证据与数据引用", "客户报告的数据支持"], deliverables: ["项目级数据包", "企业及市场快速调查", "图表与数据附录", "持续数据支持服务"] },
  academic: { label: "高校与学术研究", en: "高校与学术研究", headline: "让菌业出海研究拥有可复现、可引用、可持续的数据基础", intro: "面向高校、实验室、课题组和研究生项目，支持区域经济、国际贸易、农业产业与数据科学研究。", needs: ["论文与课题数据获取", "跨国长期序列比较", "数据方法与口径说明", "产学研及联合研究"], deliverables: ["研究级数据集与数据字典", "来源、版本和引用信息", "可复现分析样例", "联合课题与学生实践项目"] },
} as const;

export function generateStaticParams() { return Object.keys(solutions).map(slug => ({ slug })); }

export default async function SolutionPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const solution = solutions[slug as keyof typeof solutions];
  if (!solution) notFound();
  return <div className="solution-page">
    <header className="solution-nav"><Link href="/"><Image src="/inhen-tech-logo.png" alt="因恒科技" width={282} height={90} priority /></Link><nav><Link href="/">返回首页</Link><Link href="/terminal">数据终端</Link><Link className="solution-demo" href="/#contact">申请演示</Link></nav></header>
    <main>
      <section className="solution-hero"><span>{solution.en}</span><h1>{solution.headline}</h1><p>{solution.intro}</p><Link href="/#contact">讨论您的需求 →</Link></section>
      <section className="solution-detail"><div><span>01 / YOUR QUESTIONS</span><h2>{solution.label}通常需要回答什么？</h2></div><ol>{solution.needs.map((item, i) => <li key={item}><b>0{i + 1}</b><span>{item}</span></li>)}</ol></section>
      <section className="solution-delivery"><div><span>02 / DELIVERABLES</span><h2>我们可以提供的产品与交付</h2></div><div>{solution.deliverables.map((item, i) => <article key={item}><span>0{i + 1}</span><h3>{item}</h3><p>根据关注国家、行业、时间范围和使用场景配置数据字段、更新频率与交付形式。</p></article>)}</div></section>
      <section className="solution-method"><div><span>03 / METHODOLOGY</span><h2>数据可信，结论才可执行</h2></div><div><p>官方统计建立基线</p><p>市场与企业信号补充</p><p>多来源交叉核验</p><p>保留版本、口径与置信等级</p></div></section>
      <section className="solution-evidence"><div><span>04 / DATA SAMPLE</span><h2>先查看真实数据，再讨论方案</h2><p>查看菌业出海目标市场贸易金额、价格记录、HS 品类与可信度评级。</p><Link href="/market-data">进入数据中心 →</Link></div><div><span>05 / TYPICAL DELIVERY</span><h2>从问题到交付</h2><p>明确目标国家与品类后，先建立数据基线，再补充渠道、企业和政策证据，最终形成看板、名单、报告或专项研究。</p><Link href="/reports">查看研究样例 →</Link></div></section>
      <section className="solution-faq"><h2>常见问题</h2><details open><summary>可以先查看样本吗？</summary><p>可以。数据中心、大屏和报告中心均提供可直接查看的公开内容。</p></details><details><summary>能否只研究一个国家或品类？</summary><p>可以按国家、HS 品类、菌种、时间和渠道配置研究范围。</p></details></section>
      <section className="solution-bottom"><span>START A CONVERSATION</span><h2>告诉我们你的国家、行业和研究问题</h2><Link href="/#contact">申请方案沟通 →</Link></section>
    </main>
  </div>;
}
