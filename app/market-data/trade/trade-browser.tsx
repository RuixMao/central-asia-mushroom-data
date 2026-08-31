"use client";
import {useMemo,useState} from "react";
import {mirrorRecords} from "../../data";
import {centralAsiaCodes,southeastAsiaCodes,targetMarkets} from "../../market-scope";

type Region="ALL"|"SEA"|"CA";

export default function TradeBrowser(){
  const [region,setRegion]=useState<Region>("ALL");
  const [country,setCountry]=useState("ALL");
  const regionCodes=region==="SEA"?southeastAsiaCodes:region==="CA"?centralAsiaCodes:targetMarkets.map(market=>market.code);
  const latestYears=useMemo(()=>{const years=new Map<string,number>();for(const row of mirrorRecords)years.set(row.countryCode,Math.max(years.get(row.countryCode)??0,row.year??2024));return years},[]);
  const latestRecords=useMemo(()=>mirrorRecords.filter(row=>(row.year??2024)===latestYears.get(row.countryCode)),[latestYears]);
  const visible=latestRecords.filter(row=>(country==="ALL"?regionCodes.includes(row.countryCode):row.countryCode===country));
  const freshness=useMemo(()=>Array.from(new Set(latestRecords.map(row=>row.year??2024))).sort((a,b)=>b-a).map(year=>({year,countries:targetMarkets.filter(market=>latestRecords.some(row=>row.countryCode===market.code&&(row.year??2024)===year)).map(market=>market.name)})),[latestRecords]);
  const countries=new Set(visible.map(row=>row.countryCode)).size;
  const total=visible.reduce((sum,row)=>sum+Number(row.importerCifUsd??row.confirmedTradeUsd??0),0);
  function chooseRegion(next:Region){setRegion(next);setCountry("ALL")}
  return <>
    <section className="trade-filter-panel">
      <nav aria-label="贸易数据区域筛选">{[["ALL","全部市场"],["SEA","东南亚"],["CA","中亚"]].map(([value,label])=><button type="button" key={value} className={region===value?"active":""} onClick={()=>chooseRegion(value as Region)}>{label}</button>)}</nav>
      <nav aria-label="贸易数据国家筛选"><button type="button" className={country==="ALL"?"active":""} onClick={()=>setCountry("ALL")}>全部国家</button>{targetMarkets.filter(market=>regionCodes.includes(market.code)).map(market=><button type="button" key={market.code} className={country===market.code?"active":""} onClick={()=>setCountry(market.code)}>{market.name}</button>)}</nav>
      <div><span>当前展示</span><strong>{countries} 个国家 · {visible.length} 条记录</strong><span>进口额合计</span><strong>${total.toLocaleString("en-US",{maximumFractionDigits:0})}</strong></div>
      <p className="trade-freshness-note"><b>各国最新可得年度</b>{freshness.map(item=><span key={item.year}>{item.year}：{item.countries.join("、")}</span>)}</p>
    </section>
    <section className="detail-card-grid trade-country-grid">{visible.map((row,index)=><article key={`${row.countryCode}-${row.hs}-${row.year??2024}-${index}`}><span>{row.country} · HS {row.hs}</span><h2>{row.product}</h2><strong>${Number(row.importerCifUsd??row.confirmedTradeUsd??0).toLocaleString("en-US",{maximumFractionDigits:2})}</strong><dl><div><dt>年份</dt><dd>{row.year??2024}</dd></div><div><dt>净重</dt><dd>{row.officialQuantityKg?`${Number(row.officialQuantityKg).toLocaleString("en-US",{maximumFractionDigits:2})} kg`:"—"}</dd></div></dl><p>UN Comtrade · {row.confidenceBasis}</p></article>)}</section>
  </>
}
