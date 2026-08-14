"use client";
import { useEffect, useMemo, useState } from "react";
import { countryOptions, mirrorRecords } from "../data";

type MirrorItem = { countryCode:string; country:string; hs:string; product:string; importerCifUsd:number|null; chinaFobUsd:number|null; importerSource:string; mirrorSource:string; confidence:"A−"|"B+"|"B"|"C" };
const productNames:Record<string,string>={"070951":"鲜或冷藏双孢蘑菇","070959":"其他鲜或冷藏蘑菇","200310":"加工保藏蘑菇"};
const fallback:MirrorItem[]=mirrorRecords.map(record=>({...record,importerSource:"进口国申报（UN Comtrade）",mirrorSource:"中国出口镜像（UN Comtrade）",confidence:record.importerCifUsd===null?"B":"B+"}));
const money=(value:number|null)=>value===null?"暂缺":`$${value.toLocaleString("en-US")}`;
const gapRate=(importer:number|null,exporter:number|null)=>importer===null||exporter===null?null:Math.abs(importer-exporter)/Math.max(importer,exporter)*100;

export default function MirrorLiveGrid(){
  const [records,setRecords]=useState<MirrorItem[]>(fallback); const [live,setLive]=useState(false);
  useEffect(()=>{fetch("/api/trade?mode=mirror&year=2024").then(response=>response.ok?response.json() as Promise<{records?:MirrorItem[]}>:Promise.reject()).then(payload=>{if(payload.records?.length){setRecords(payload.records);setLive(true)}}).catch(()=>{})},[]);
  const countries=useMemo(()=>countryOptions.filter(country=>country.code!=="ALL"),[]);
  return <><div className="mirror-source-state"><b>{live?"多源数据已连接":"正在使用已核验基线"}</b><span>本国进口申报优先；缺失时保留中国出口镜像，不再把缺报等同于零贸易。</span></div><div className="mirror-country-list">{countries.map(country=>{const items=records.filter(record=>record.countryCode===country.code&&(record.importerCifUsd!==null||record.chinaFobUsd!==null));return <section className="mirror-country" key={country.code}><header><div><b>{country.label}</b><span>{country.code}</span></div><small>{items.length?`${items.length} 个有证据品类`:"正在扩展来源"}</small></header>{items.length?<div className="mirror-grid">{items.map(record=>{const gap=gapRate(record.importerCifUsd,record.chinaFobUsd);const status=record.importerCifUsd===null?"进口国侧暂缺 · 已有出口镜像":gap!==null&&gap>=70?"显著差异":"交叉核验可用";return <article key={`${record.countryCode}-${record.hs}`}><span className="mirror-category">{productNames[record.hs]??record.product}</span><h3>HS {record.hs} · 置信度 {record.confidence}</h3><div><p>进口方 CIF<b>{money(record.importerCifUsd)}</b><small>{record.importerSource}</small></p><p>中国出口 FOB<b>{money(record.chinaFobUsd)}</b><small>{record.mirrorSource}</small></p></div><strong>{gap===null?"—":`${gap.toFixed(1)}%`}<small>{gap===null?"单侧证据，暂不计算差异":"镜像差异率"}</small></strong><i>{status}</i></article>})}</div>:<div className="mirror-empty"><b>暂无达到发布门槛的数据</b><p>正在从本国统计机构、中国海关及主要伙伴国镜像继续补齐。</p></div>}</section>})}</div></>;
}
