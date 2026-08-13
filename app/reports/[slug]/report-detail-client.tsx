"use client";
import { useEffect, useState, type ReactNode } from "react";
import Link from "next/link";

type Report={slug:string;title:string;type:string;country:string;summary:string;body:string;publishedAt:string|number|Date};

function InlineText({text}:{text:string}){
  const parts=text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).filter(Boolean);
  return <>{parts.map((part,i)=>part.startsWith("**")&&part.endsWith("**")?<strong key={i}>{part.slice(2,-2)}</strong>:part.startsWith("`")&&part.endsWith("`")?<code key={i}>{part.slice(1,-1)}</code>:part as ReactNode)}</>;
}

function ReportBody({body}:{body:string}){
  return <div className="report-body">{body.split(/\r?\n/).map((line,i)=>{
    const text=line.trim();
    if(!text)return <span className="report-spacer" key={i}/>;
    if(text.startsWith("### "))return <h3 key={i}><InlineText text={text.slice(4)}/></h3>;
    if(text.startsWith("## "))return <h2 key={i}><InlineText text={text.slice(3)}/></h2>;
    if(text.startsWith("# "))return <h2 key={i}><InlineText text={text.slice(2)}/></h2>;
    if(text.startsWith("> "))return <blockquote key={i}><InlineText text={text.slice(2)}/></blockquote>;
    const numbered=text.match(/^(\d+)\.\s+(.+)$/);
    if(numbered)return <div className="report-numbered" key={i}><b>{numbered[1].padStart(2,"0")}</b><p><InlineText text={numbered[2]}/></p></div>;
    return <p key={i}><InlineText text={text.replace(/\s{2}$/g,"")}/></p>;
  })}</div>;
}

export default function ReportDetailClient({slug}:{slug:string}){
  const [report,setReport]=useState<Report|null>(null),[error,setError]=useState("");
  useEffect(()=>{
    const controller=new AbortController();
    fetch(`/api/ingest/report?slug=${encodeURIComponent(slug)}`,{signal:controller.signal}).then(async response=>{
      const payload=await response.json() as {records?:Report[]};
      if(!response.ok||!payload.records?.[0])throw new Error("未找到这份报告");
      setReport(payload.records[0]);
    }).catch(reason=>{if(reason instanceof Error&&reason.name!=="AbortError")setError(reason.message)});
    return ()=>controller.abort();
  },[slug]);
  if(error)return <section className="report-state"><b>{error}</b><Link href="/reports">返回报告中心 →</Link></section>;
  if(!report)return <section className="report-state" aria-live="polite">正在读取报告…</section>;
  const date=new Date(report.publishedAt).toLocaleDateString("zh-CN");
  return <><Link className="report-back" href="/reports">← 返回报告中心</Link><article className="report-detail"><header><div className="tag-row"><b>{report.type}</b><b>{report.country}</b></div><h1>{report.title}</h1><p>{report.summary}</p><small>{date} · 数据来源：因恒科技</small></header><ReportBody body={report.body}/></article></>;
}
