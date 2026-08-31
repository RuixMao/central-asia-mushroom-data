import ProductShell from "../../product-shell";
import Link from "next/link";
import {caseTopics} from "./case-data";
export default function Page(){return <ProductShell><main className="saas-main"><section className="saas-hero compact"><span>出海案例</span><h1>食用菌跨境项目案例库</h1><p>按出口、海外项目、菌包产能和智慧设施浏览公开案例。</p></section><section className="detail-card-grid case-topic-grid">{caseTopics.map(topic=><article key={topic.slug}><span>{topic.label}</span><h2>{topic.title}</h2><p>{topic.intro}</p><strong>{topic.cases.length} 个公开案例</strong><Link href={`/expand/cases/${topic.slug}`}>查看案例与原文 →</Link></article>)}</section></main></ProductShell>}
