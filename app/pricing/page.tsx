import Link from "next/link";
import ProductShell from "../product-shell";

const services=[
  {status:"可直接使用",name:"免费公开数据",desc:"查看五国贸易基线、今日有效价格、来源和数据缺口。",deliverables:["公开价格与贸易样例","来源、口径与更新时间","日报与市场信号"]},
  {status:"可申请",name:"国别市场验证包",desc:"围绕一个国家和明确产品，整理市场规模、价格、风险与待验证问题。",deliverables:["国别市场判断","证据与风险清单","下一步验证任务"]},
  {status:"可申请",name:"持续市场监测",desc:"按目标国家、品类和渠道持续跟踪公开价格与贸易变化。",deliverables:["定期价格观察","变化与异常提示","可追溯市场简报"]},
  {status:"按项目确认",name:"定制研究与合作验证",desc:"围绕具体进入假设开展渠道、物流、准入或合作条件核验。",deliverables:["研究范围确认","阶段性交付","结论与后续建议"]},
];
export default function Pricing(){return <ProductShell><main className="saas-main"><section className="saas-hero compact center"><span>SERVICES & DELIVERABLES</span><h1>服务与交付方式</h1><p>根据现有数据和真实验证能力确定交付范围；暂不承诺未形成闭环的 API、邮件提醒或企业级 SLA。</p></section><section className="service-delivery-grid">{services.map(item=><article key={item.name}><span>{item.status}</span><h2>{item.name}</h2><p>{item.desc}</p><ul>{item.deliverables.map(x=><li key={x}>{x}</li>)}</ul><Link href={item.name==="免费公开数据"?"/market":"/expand/contact"}>{item.name==="免费公开数据"?"查看公开数据":"准备验证需求"} →</Link></article>)}</section><section className="faq"><h2>交付原则</h2><details open><summary>是否直接提供买家或成交数据？</summary><p>只有在来源、授权和验证方式明确后才纳入交付；规划中的买家图谱和成交数据库目前属于共建能力。</p></details><details><summary>价格是否等于实际成交价？</summary><p>不是。公开页面记录为挂牌观察价，真实成交价需要结合采购量、规格、账期和渠道进一步验证。</p></details><details><summary>缺失数据如何处理？</summary><p>平台展示最近有效日期、缺口原因与证据状态，不使用零值或未经核验的估算填补。</p></details></section></main></ProductShell>}
