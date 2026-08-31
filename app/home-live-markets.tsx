"use client";
import Link from "next/link";
import {useEffect,useMemo,useState} from "react";
import {countryNames,latestByCountry,loadLivePrices,marketCodesFromRows,marketName,prioritizedRows,rowPrice,speciesLabel,type LivePriceRow} from "./market-display";
import {centralAsiaCodes,southeastAsiaCodes} from "./market-scope";
import {marketReadiness} from "./market-readiness";

type Region="ALL"|"CA"|"SEA";

type MarketSignal={
  code:string;
  title:string;
  metric:string;
  meaning:string;
  action:string;
};

export function HomeSignalOverview(){
  const [rows,setRows]=useState<LivePriceRow[]>([]);
  const [ready,setReady]=useState(false);
  useEffect(()=>{loadLivePrices().then(setRows).catch(()=>setRows([])).finally(()=>setReady(true))},[]);
  const latest=useMemo(()=>latestByCountry(rows),[rows]);
  const signals=useMemo(()=>{
    const build=(code:string):MarketSignal|null=>{
      const countryRows=latest.filter(row=>row.country===code&&row.is_current!==false);
      if(!countryRows.length)return null;
      const channels=new Set(countryRows.map(row=>row.platform_name)).size;
      const species=new Set(countryRows.map(row=>speciesLabel(row.species_id,false))).size;
      return {
        code,
        title:`${marketName(countryRows[0])}已有可比较价格`,
        metric:rowPrice(prioritizedRows(countryRows,1)[0]),
        meaning:`${channels} 个渠道，覆盖 ${species} 个品种。`,
        action:`查看${marketName(countryRows[0])}市场`,
      };
    };
    return marketCodesFromRows(latest).sort((a,b)=>latest.filter(row=>row.country===b&&row.is_current!==false).length-latest.filter(row=>row.country===a&&row.is_current!==false).length).map(build).filter((item):item is MarketSignal=>item!=null).slice(0,3);
  },[latest]);
  const visibleSignals=signals;
  return <section className="decision-section home-signal-section">
    <header><span>市场机会</span><h2>近期值得关注的市场</h2></header>
    {!ready?<div className="price-skeleton" aria-label="市场信号加载中">{Array.from({length:3},(_,i)=><i key={i}/>)}</div>:visibleSignals.length?<div className="home-signal-grid">{visibleSignals.map((signal,index)=><article key={signal.code}><span>{String(index+1).padStart(2,"0")} · {countryNames[signal.code]??signal.code}</span><h3>{signal.title}</h3><strong>{signal.metric}</strong><p>{signal.meaning}</p><Link href={`/markets/${signal.code}`}>{signal.action} →</Link></article>)}</div>:<p className="market-neutral-state">价格数据更新后将在此显示。</p>}
    <Link className="section-link" href="/opportunities">查看全部市场机会 →</Link>
  </section>
}

export function HomeMarketMatrix(){
 const [rows,setRows]=useState<LivePriceRow[]>([]);
 const [ready,setReady]=useState(false);
 useEffect(()=>{loadLivePrices().then(setRows).catch(()=>setRows([])).finally(()=>setReady(true))},[]);
 const markets=useMemo(()=>marketCodesFromRows(rows).filter(code=>rows.some(row=>row.country===code)).map(code=>{const items=rows.filter(row=>row.country===code);return {code,name:marketName(items[0]),state:marketReadiness(items),updated:items.reduce((date,row)=>row.observation_date>date?row.observation_date:date,"")}}),[rows]);
 return <section className="decision-section home-market-matrix"><header><span>市场覆盖</span><h2>价格数据覆盖市场</h2></header>{!ready?<div className="price-skeleton"><i/><i/><i/></div>:markets.length?<div className="home-market-matrix-grid">{markets.map(market=><Link href={`/markets/${market.code}`} key={market.code}><b>{market.name}</b><span>{market.state.level==="L0"?"已有公开报价":"市场信息持续更新"}</span><small>{market.updated?`更新于 ${market.updated}`:"查看市场信息"}</small></Link>)}</div>:<p className="market-neutral-state">价格数据更新后将在此显示。</p>}</section>
}

export function HomePriceOverview(){
  const [rows,setRows]=useState<LivePriceRow[]>([]);
  const [ready,setReady]=useState(false);
  const [region,setRegion]=useState<Region>("ALL");
  const [country,setCountry]=useState("ALL");
  useEffect(()=>{loadLivePrices().then(setRows).catch(()=>setRows([])).finally(()=>setReady(true))},[]);
  const dataCodes=useMemo(()=>marketCodesFromRows(rows).filter(code=>rows.some(row=>row.country===code)),[rows]);
  const regionCodes=region==="SEA"?dataCodes.filter(code=>southeastAsiaCodes.includes(code)):region==="CA"?dataCodes.filter(code=>centralAsiaCodes.includes(code)):dataCodes;
  const latest=useMemo(()=>latestByCountry(rows),[rows]);
  const visible=useMemo(()=>{
    const codes=country==="ALL"?regionCodes:[country];
    return codes.flatMap(code=>prioritizedRows(latest.filter(row=>row.country===code&&row.is_current!==false),2));
  },[latest,country,regionCodes]);
  function chooseRegion(nextRegion:Region){setRegion(nextRegion);setCountry("ALL")}
  return <section className="decision-section home-price-overview" id="prices">
    <header><span>目标市场价格速览</span><h2>先看各国具体报价</h2><p>先选择区域，再按国家查看当地公开价格与代表性渠道。</p></header>
    <nav className="price-region-tabs" aria-label="选择价格区域">{[["ALL","全部市场"],["CA","中亚"],["SEA","东南亚"]].map(([value,label])=><button key={value} type="button" className={region===value?"active":""} aria-pressed={region===value} onClick={()=>chooseRegion(value as Region)}>{label}</button>)}</nav>
    <nav className="price-country-tabs" aria-label="选择国家"><button type="button" className={country==="ALL"?"active":""} aria-pressed={country==="ALL"} onClick={()=>setCountry("ALL")}>全部国家</button>{regionCodes.map(code=><button key={code} type="button" className={country===code?"active":""} aria-pressed={country===code} onClick={()=>setCountry(code)}>{countryNames[code]}</button>)}</nav>
    {!ready?<div className="price-skeleton" aria-label="价格加载中">{Array.from({length:5},(_,i)=><i key={i}/>)}</div>:<div className="home-price-grid">{visible.map((row,index)=><article key={`${row.country}-${row.species_id}-${index}`}><span>{marketName(row)}</span><h3>{speciesLabel(row.species_id)}</h3><strong>{rowPrice(row)}</strong><small>{row.platform_name} · 更新于 {row.observation_date}</small><Link href={`/markets/${row.country}#prices`}>查看该国价格 →</Link></article>)}</div>}
    <Link className="section-link" href="/market">查看全部市场价格 →</Link>
  </section>
}

