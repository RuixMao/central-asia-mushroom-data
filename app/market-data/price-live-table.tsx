"use client";
import { useEffect, useMemo, useState } from "react";

type PriceData = { variety?: string; form?: string; spec?: string; channel?: string; price_local?: number; currency?: string; price_cny?: number; observed_at?: string; source_url?: string; status?: "live"|"gap"; reason?: string };
type Snapshot = { id: string; country: string; data: PriceData; source: string };
const countryNames: Record<string,string> = {KZ:"哈萨克斯坦",UZ:"乌兹别克斯坦",KG:"吉尔吉斯斯坦",TJ:"塔吉克斯坦",TM:"土库曼斯坦"};
const fallback: Snapshot[] = [
  {id:"kz-1",country:"KZ",source:"Arbuz / Carefood",data:{variety:"双孢菇",form:"鲜品",spec:"1kg",channel:"电商/商超",currency:"KZT",observed_at:"2026-08-11",source_url:"https://arbuz.kz/",status:"live"}},
  {id:"kg-1",country:"KG",source:"Globus Online",data:{variety:"双孢菇",form:"鲜品",spec:"1kg",channel:"商超",price_local:520,currency:"KGS",observed_at:"2026-08-11",source_url:"https://globus-online.kg/",status:"live"}},
  {id:"tj-1",country:"TJ",source:"Zudbiyor",data:{variety:"双孢菇",form:"鲜品",spec:"1kg",channel:"即时零售",price_local:86.3,currency:"TJS",observed_at:"2026-08-11",source_url:"https://zudbiyor.tj/product/141",status:"live"}},
];
const countries = [["ALL","全部国家"],...Object.entries(countryNames)];
const varieties = ["全部菌种","双孢菇","平菇","香菇","金针菇","木耳"];

export default function PriceLiveTable(){
  const [records,setRecords]=useState<Snapshot[]>(fallback),[country,setCountry]=useState("ALL"),[variety,setVariety]=useState("全部菌种"),[fallbackMode,setFallbackMode]=useState(true);
  useEffect(()=>{fetch("/api/ingest/snapshot?metric=price_retail&latest=1&limit=500").then(r=>r.ok?r.json() as Promise<{records?:Snapshot[]}>:Promise.reject()).then(p=>{if(p.records?.length){setRecords(p.records);setFallbackMode(false)}}).catch(()=>{})},[]);
  const visible=useMemo(()=>records.filter(r=>(country==="ALL"||r.country===country)&&(variety==="全部菌种"||r.data.variety===variety)),[records,country,variety]);
  const live=visible.filter(r=>r.data.status!=="gap"), gaps=visible.filter(r=>r.data.status==="gap");
  const gapText=`📡 采集缺口 — 暂未在${country==="ALL"?"所选国家":countryNames[country]}电商发现${variety==="全部菌种"?"该菌种":variety}在售`;
  return <><div className="live-price-filters"><label>国家<select value={country} onChange={e=>setCountry(e.target.value)}>{countries.map(([v,l])=><option value={v} key={v}>{l}</option>)}</select></label><label>菌种<select value={variety} onChange={e=>setVariety(e.target.value)}>{varieties.map(v=><option value={v} key={v}>{v}</option>)}</select></label><small>{fallbackMode?"显示已验证基线":"D1 自动采集数据"}</small></div>{live.length?<div className="live-price-table"><div className="live-price-row head"><b>国家</b><b>菌种</b><b>形态</b><b>规格</b><b>渠道</b><b>原币价格</b><b>¥折算</b><b>观察日期</b><b>来源</b></div>{live.map(r=><div className="live-price-row" key={r.id}><span>{countryNames[r.country]}</span><span>{r.data.variety}</span><span>{r.data.form}</span><span>{r.data.spec}</span><span>{r.data.channel}</span><span>{r.data.price_local==null?"待补":`${r.data.price_local} ${r.data.currency}`}</span><span>{r.data.price_cny==null?"待补":`¥${r.data.price_cny}`}</span><span>{r.data.observed_at}</span><span>{r.data.source_url?<a href={r.data.source_url} target="_blank" rel="noreferrer">{r.source} ↗</a>:r.source}</span></div>)}</div>:<div className="price-gap">{gapText}</div>}{gaps.map(r=><div className="price-gap" key={r.id}>📡 采集缺口 — {countryNames[r.country]} {r.data.variety}：{r.data.reason}</div>)}</>;
}
