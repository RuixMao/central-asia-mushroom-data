"use client";
import { useEffect, useState } from "react";
import { reports as fallbackReports } from "../saas-data";

type Report={id?:string;slug?:string;title:string;type:string;country:string;summary:string;publishedAt?:string|number|Date;date?:string};
export default function ReportsClient({filter="all"}:{filter?:"all"|"daily"|"weekly"|"monthly"|"quarterly"|"annual"}){
  const fallback:Report[]=fallbackReports.map((r,i)=>({...r,id:`fallback-${i}`}));
  const fallbackDate=fallbackReports[0]?.date??"";
  const [items,setItems]=useState<Report[]>(fallback);
  const refresh=()=>fetch("/api/ingest/report").then(r=>r.ok?r.json() as Promise<{records?:Report[]}>:Promise.reject()).then(p=>{if(p.records?.length)setItems(p.records)}).catch(()=>{});
  useEffect(()=>{refresh()},[]);
  const visible=filter==="all"?items:items.filter(item=>item.type.toLowerCase().includes(filter));
  const latest=items.find(item=>item.slug);
  return <><div className="report-generator"><div><b>最新市场研究</b><small>查看最近发布的中亚菌类市场报告与行动建议</small></div>{latest?.slug&&<a href={`/reports/${encodeURIComponent(latest.slug)}`} data-native-navigation="true">查看最新日报 →</a>}</div><section className="report-list">{visible.map((report,i)=><article key={report.id??report.title}><span>{String(i+1).padStart(2,"0")}</span><div><div className="tag-row"><b>{report.type}</b><b>{report.country}</b></div><h2>{report.title}</h2><p>{report.summary}</p><small>{report.date??(report.publishedAt?new Date(report.publishedAt).toLocaleDateString("zh-CN"):fallbackDate)} · 数据来源：因恒科技</small></div>{report.slug?<a href={`/reports/${encodeURIComponent(report.slug)}`} data-native-navigation="true">阅读全文 →</a>:<span className="report-unavailable">摘要预览</span>}</article>)}</section></>;
}
