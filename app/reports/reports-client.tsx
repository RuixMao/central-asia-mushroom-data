"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { reports as fallbackReports } from "../saas-data";

type Report = {id?:string;slug?:string;title:string;type:string;country:string;summary:string;publishedAt?:string|number|Date;date?:string;aiGenerated?:boolean};
export default function ReportsClient(){
  const fallback:Report[]=fallbackReports.map((r,i)=>({...r,id:`fallback-${i}`,aiGenerated:true}));
  const [items,setItems]=useState<Report[]>(fallback);
  useEffect(()=>{fetch("/api/ingest/report").then(r=>r.ok?r.json() as Promise<{records?:Report[]}>:Promise.reject()).then(p=>{if(p.records?.length)setItems(p.records)}).catch(()=>{})},[]);
  return <section className="report-list">{items.map((report,i)=><article key={report.id??report.title}><span>0{i+1}</span><div><div className="tag-row"><b>{report.type}</b><b>{report.country}</b>{report.aiGenerated!==false&&<b>AI 生成</b>}</div><h2>{report.title}</h2><p>{report.summary}</p><small>{report.date??new Date(report.publishedAt??Date.now()).toLocaleDateString("zh-CN")} · 数据来源：自动采集管线</small></div><Link href={report.slug?`/reports/${report.slug}`:"/pricing"}>阅读全文 →</Link></article>)}</section>;
}
