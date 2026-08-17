"use client";

import { useEffect, useMemo, useState } from "react";
import { mirrorRecords, opportunities } from "./data";

type PriceRow = { observation_date:string; country:string; country_name?:string; species_id:string; species_name?:string; platform_name:string; original_title:string; normalized_usd_per_kg:number|null };
type Report = { slug?:string; title:string; type:string; date?:string; publishedAt?:string|number|Date };
const countryNames:Record<string,string>={KZ:"哈萨克斯坦",UZ:"乌兹别克斯坦",KG:"吉尔吉斯斯坦",TJ:"塔吉克斯坦",TM:"土库曼斯坦"};
const countryCodes=["KZ","UZ","KG","TJ","TM"];
const money=(value:number)=>value?value>=1_000_000?`$${(value/1_000_000).toFixed(2)}M`:`$${Math.round(value/1000).toLocaleString("zh-CN")}K`:"—";
const range=(values:number[])=>values.length?`$${Math.min(...values).toFixed(2)}–$${Math.max(...values).toFixed(2)}/kg`:"—";

function usePrices(){
  const [rows,setRows]=useState<PriceRow[]>([]); const [ready,setReady]=useState(false);
  useEffect(()=>{fetch("/api/powerbi?table=prices",{cache:"no-store"}).then(r=>r.ok?r.json():Promise.reject()).then(p=>setRows(p.records??[])).catch(()=>setRows([])).finally(()=>setReady(true))},[]);
  const latest=useMemo(()=>rows.reduce((d,r)=>r.observation_date>d?r.observation_date:d,""),[rows]);
  const today=useMemo(()=>rows.filter(r=>r.observation_date===latest),[rows,latest]);
  return {rows,today,latest,ready};
}

export function MarketLivePreview(){
  const {today,latest,ready}=usePrices();
  const species=useMemo(()=>Array.from(new Map(today.map(r=>[r.species_id,r.species_name??r.species_id])).entries()).map(([id,name])=>({id,name,count:today.filter(r=>r.species_id===id).length})),[today]);
  return <section className="theme-data-grid">
    <article className="theme-data-card wide"><header><div><span>TODAY PRICE SNAPSHOT</span><h2>今日价格摘要</h2></div><small>{latest||"—"} · 有效标准公斤价</small></header><div className="theme-table"><div className="theme-row head"><span>国家</span><span>品类</span><span>USD/kg</span><span>平台</span></div>{today.slice(0,10).map((r,i)=><div className="theme-row" key={`${r.country}-${r.platform_name}-${i}`}><span>{r.country_name??countryNames[r.country]}</span><span>{r.species_name??r.species_id}</span><strong>{r.normalized_usd_per_kg==null?"—":`$${Number(r.normalized_usd_per_kg).toFixed(2)}`}</strong><span>{r.platform_name}</span></div>)}{ready&&!today.length&&<p className="theme-empty">— 暂无今日有效价格</p>}</div></article>
    <article className="theme-data-card"><header><div><span>SPECIES SCAN</span><h2>新品与品类扫描</h2></div></header>{species.length?<div className="theme-chip-list">{species.map(s=><div key={s.id}><b>{s.name}</b><span>{s.count} 条有效观察</span></div>)}</div>:<p className="theme-empty">— 暂无可核验新品记录</p>}<a href="/market/scan">查看完整品类扫描 →</a></article>
  </section>;
}

export function InsightsLivePreview(){
  const {today,latest}=usePrices();
  const hs=useMemo(()=>["070951","070959","200310"].map(code=>({code,total:mirrorRecords.filter(r=>r.hs===code).reduce((s,r)=>s+Number(r.importerCifUsd??r.confirmedTradeUsd??0),0)})),[]);
  return <section className="theme-data-grid three">
    <article className="theme-data-card"><header><div><span>COUNTRY DEMAND</span><h2>国别需求画像</h2></div><small>价格截至 {latest||"—"}</small></header><div className="theme-country-list">{countryCodes.map(code=>{const trade=mirrorRecords.filter(r=>r.countryCode===code);const total=trade.reduce((s,r)=>s+Number(r.importerCifUsd??r.confirmedTradeUsd??0),0);const china=trade.reduce((s,r)=>s+Number(r.chinaFobUsd??0),0);const prices=today.filter(r=>r.country===code).map(r=>Number(r.normalized_usd_per_kg)).filter(Number.isFinite);return <div key={code}><b>{countryNames[code]}</b><span>进口 {money(total)}</span><span>中国占比 {total&&trade.some(r=>r.chinaFobUsd!=null)?`${(china/total*100).toFixed(1)}%`:"—"}</span><span>零售价 {range(prices)}</span></div>})}</div></article>
    <article className="theme-data-card"><header><div><span>HS STRUCTURE</span><h2>规模与品类结构</h2></div></header><div className="theme-metric-list">{hs.map(item=><div key={item.code}><span>HS {item.code}</span><strong>{money(item.total)}</strong></div>)}</div><small className="theme-source">来源：UN Comtrade 2024 进口申报及伙伴国镜像记录；缺报国家采用已确认伙伴国汇总。</small></article>
    <article className="theme-data-card"><header><div><span>CHANNEL COVERAGE</span><h2>平台与覆盖品类</h2></div></header><div className="theme-country-list">{countryCodes.map(code=>{const rows=today.filter(r=>r.country===code);return <div key={code}><b>{countryNames[code]}</b><span>{new Set(rows.map(r=>r.platform_name)).size||"—"} 个渠道</span><span>{new Set(rows.map(r=>r.species_id)).size||"—"} 个菌种</span><span>{rows.length?"今日有效":"今日缺口"}</span></div>})}</div></article>
  </section>;
}

export function ExpandLivePreview(){
  const [report,setReport]=useState<Report|null>(null);
  useEffect(()=>{fetch("/api/ingest/report",{cache:"no-store"}).then(r=>r.ok?r.json():Promise.reject()).then(p=>setReport(p.records?.[0]??null)).catch(()=>{})},[]);
  return <section className="theme-data-grid four">
    <article className="theme-data-card"><span>案例图谱</span><h2>企业拓展路径</h2><p className="theme-empty">案例收集中</p><small>仅收录具备公开来源、可回溯核验的企业案例。</small><a href="/expand/cases">查看案例库 →</a></article>
    <article className="theme-data-card"><span>每日菌情</span><h2>{report?.title??"最新报告暂未发布"}</h2><p>{report?`${report.type} · ${report.date??(report.publishedAt?new Date(report.publishedAt).toLocaleDateString("zh-CN"):"—")}`:"—"}</p><a href={report?.slug?`/reports/${encodeURIComponent(report.slug)}`:"/reports"}>查看市场报告 →</a></article>
    <article className="theme-data-card"><span>商机雷达</span><h2>已验证需求信号</h2><div className="theme-signal-list">{opportunities.slice(0,3).map(o=><div key={o.id}><b>{o.country} · {o.product}</b><span>{o.status}</span><small>{o.signal}</small></div>)}</div><a href="/expand/radar">打开商机雷达 →</a></article>
    <article className="theme-data-card"><span>合作对接</span><h2>提交出海需求</h2><p>面向产能方、渠道商、技术与服务机构。</p><a className="theme-primary-link" href="/expand/contact">发起合作对接 →</a></article>
  </section>;
}
