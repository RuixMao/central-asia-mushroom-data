"use client";
import Link from "next/link";
import {useEffect,useMemo,useState} from "react";
import {allCodes,countryNames,latestByCountry,loadLivePrices,prioritizedRows,rowPrice,speciesLabel,type LivePriceRow} from "./market-display";

type Region="ALL"|"CA"|"SEA";

export function HomePriceOverview(){
  const [rows,setRows]=useState<LivePriceRow[]>([]);
  const [ready,setReady]=useState(false);
  const [region,setRegion]=useState<Region>("ALL");
  const [country,setCountry]=useState("ALL");
  useEffect(()=>{loadLivePrices().then(setRows).finally(()=>setReady(true))},[]);
  const regionCodes=region==="SEA"?allCodes.slice(0,5):region==="CA"?allCodes.slice(5):allCodes;
  const selectedCodes=country==="ALL"?regionCodes:[country];
  const latest=useMemo(()=>latestByCountry(rows),[rows]);
  const visible=useMemo(()=>selectedCodes.flatMap(code=>prioritizedRows(latest.filter(row=>row.country===code),2)),[latest,country,region]);
  function chooseRegion(nextRegion:Region){setRegion(nextRegion);setCountry("ALL")}
  return <section className="decision-section home-price-overview" id="prices">
    <header><span>目标市场价格速览</span><h2>先看各国具体报价</h2><p>先选择区域，再按国家查看当地公开价格与代表性渠道。</p></header>
    <nav className="price-region-tabs" aria-label="选择价格区域">{[["ALL","全部市场"],["CA","中亚"],["SEA","东南亚"]].map(([value,label])=><button key={value} type="button" className={region===value?"active":""} aria-pressed={region===value} onClick={()=>chooseRegion(value as Region)}>{label}</button>)}</nav>
    <nav className="price-country-tabs" aria-label="选择国家"><button type="button" className={country==="ALL"?"active":""} aria-pressed={country==="ALL"} onClick={()=>setCountry("ALL")}>全部国家</button>{regionCodes.map(code=><button key={code} type="button" className={country===code?"active":""} aria-pressed={country===code} onClick={()=>setCountry(code)}>{countryNames[code]}</button>)}</nav>
    {!ready?<div className="price-skeleton" aria-label="价格加载中">{Array.from({length:5},(_,i)=><i key={i}/>)}</div>:<div className="home-price-grid">{visible.map((row,index)=><article key={`${row.country}-${row.species_id}-${index}`}><span>{countryNames[row.country]}</span><h3>{speciesLabel(row.species_id)}</h3><strong>{rowPrice(row)}</strong><small>{row.platform_name} · 更新于 {row.observation_date}</small><Link href={`/markets/${row.country}#prices`}>查看该国价格 →</Link></article>)}</div>}
    <Link className="section-link" href="/market">查看全部市场价格 →</Link>
  </section>
}

export function HomeMarketCards(){const [rows,setRows]=useState<LivePriceRow[]>([]);useEffect(()=>{loadLivePrices().then(setRows)},[]);return <div className="focus-market-grid">{[{code:"LA",name:"老挝",risk:"批量成交价、清关条件与末端配送成本会影响实际利润"},{code:"KZ",name:"哈萨克斯坦",risk:"冷链到岸成本及零售挂牌价与真实成交价存在差异"}].map(item=>{const countryRows=latestByCountry(rows).filter(row=>row.country===item.code);const prices=countryRows.map(row=>row.normalized_usd_per_kg).filter((value):value is number=>value!=null);const channels=new Set(countryRows.map(row=>row.platform_name)).size;const species=new Set(countryRows.map(row=>speciesLabel(row.species_id,false))).size;return <article key={item.code}><div className="focus-market-title"><span>{item.code}</span><h3>{item.name}</h3><em>{countryRows.length?`已有 ${countryRows.length} 条价格`:"市场信息"}</em></div><strong>{countryRows.length?`${channels} 个渠道覆盖 ${species} 个品种，可直接比较当地报价。`:"查看该市场的贸易、价格与渠道信息。"}</strong><dl><div><dt>公开价格区间</dt><dd>{prices.length?`$${Math.min(...prices).toFixed(2)}–$${Math.max(...prices).toFixed(2)}/kg`:countryRows[0]?rowPrice(countryRows[0]):"查看市场数据"}</dd></div><div><dt>渠道数</dt><dd>{channels||"查看详情"}</dd></div><div><dt>品种数</dt><dd>{species||"查看详情"}</dd></div></dl><p><b>您需要注意：</b>{item.risk}</p><a href={`/markets/${item.code}#prices`}>查看国家市场 →</a></article>})}</div>}
