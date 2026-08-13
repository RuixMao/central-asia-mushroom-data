"use client";
import { useEffect, useState } from "react";
import { reports as fallbackReports } from "../saas-data";

type Report={id?:string;slug?:string;title:string;type:string;country:string;summary:string;publishedAt?:string|number|Date;date?:string};
export default function ReportsClient(){
  const fallback:Report[]=fallbackReports.map((r,i)=>({...r,id:`fallback-${i}`}));
  const fallbackDate=fallbackReports[0]?.date??"";
  const [items,setItems]=useState<Report[]>(fallback),[generating,setGenerating]=useState(false),[message,setMessage]=useState("");
  const refresh=()=>fetch("/api/ingest/report").then(r=>r.ok?r.json() as Promise<{records?:Report[]}>:Promise.reject()).then(p=>{if(p.records?.length)setItems(p.records)}).catch(()=>{});
  useEffect(()=>{refresh()},[]);
  async function generateDaily(){
    setGenerating(true);setMessage("正在整理今日价格并生成客户日报…");
    try{const response=await fetch("/api/reports/generate-daily",{method:"POST"});const result=await response.json() as {error?:string;title?:string;priceCount?:number};if(!response.ok)throw new Error(result.error||"生成失败");setMessage(`日报已生成：${result.title}（使用 ${result.priceCount} 条价格）`);await refresh()}catch(error){setMessage(error instanceof Error?error.message:"生成失败")}finally{setGenerating(false)}
  }
  return <><div className="report-generator"><div><b>今日价格日报</b><small>读取今日全部有效价格，整理为面向客户的市场日报</small></div><button disabled={generating} onClick={generateDaily}>{generating?"生成中…":"生成今日日报"}</button>{message&&<p role="status">{message}</p>}</div><section className="report-list">{items.map((report,i)=><article key={report.id??report.title}><span>{String(i+1).padStart(2,"0")}</span><div><div className="tag-row"><b>{report.type}</b><b>{report.country}</b></div><h2>{report.title}</h2><p>{report.summary}</p><small>{report.date??(report.publishedAt?new Date(report.publishedAt).toLocaleDateString("zh-CN"):fallbackDate)} · 数据来源：因恒科技</small></div>{report.slug?<a href={`/reports/${encodeURIComponent(report.slug)}`} data-native-navigation="true">阅读全文 →</a>:<span className="report-unavailable">摘要预览</span>}</article>)}</section></>;
}
