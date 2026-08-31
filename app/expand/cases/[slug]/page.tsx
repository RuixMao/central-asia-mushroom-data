import {notFound} from "next/navigation";
import Link from "../../../native-link";
import ProductShell from "../../../product-shell";
import {caseTopics,getCaseTopic} from "../case-data";

export function generateStaticParams(){return caseTopics.map(topic=>({slug:topic.slug}))}

export default async function Page({params}:{params:Promise<{slug:string}>}){
  const topic=getCaseTopic((await params).slug);
  if(!topic)notFound();
  return <ProductShell><main className="saas-main"><section className="saas-hero compact"><span>{topic.label}</span><h1>{topic.title}</h1><p>{topic.intro}</p><div className="market-anchor-nav">{caseTopics.map(item=><Link href={`/expand/cases/${item.slug}`} key={item.slug}>{item.label}</Link>)}</div></section><section className="case-study-list">{topic.cases.map(item=><article key={item.title}><header><div><span>{item.market}</span><h2>{item.title}</h2></div><small>{item.date}</small></header><ul>{item.facts.map(fact=><li key={fact}>{fact}</li>)}</ul><a href={item.url} target="_blank" rel="noreferrer">{item.source} · 查看原文 →</a></article>)}</section></main></ProductShell>
}
