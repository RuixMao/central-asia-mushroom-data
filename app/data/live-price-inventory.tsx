"use client";
import {useEffect,useMemo,useState} from "react";
import {loadLivePrices,speciesLabel,type LivePriceRow} from "../market-display";

export default function LivePriceInventory({mode}:{mode:"kpis"|"species"}){
 const [rows,setRows]=useState<LivePriceRow[]>([]);
 useEffect(()=>{loadLivePrices().then(setRows).catch(()=>setRows([]))},[]);
 const active=useMemo(()=>rows.filter(row=>row.status!=="archived"&&row.status!=="deleted"),[rows]);
 const species=useMemo(()=>Array.from(new Set(active.map(row=>row.species_id))).map(speciesLabel),[active]);
 const channels=useMemo(()=>new Set(active.map(row=>`${row.country}:${row.platform_name}`)).size,[active]);
 if(mode==="kpis")return <><article><span>市场品类</span><strong>{species.length} 类</strong><small>由当前价格数据自动汇总</small></article><article><span>价格渠道</span><strong>{channels} 个</strong><small>随价格记录增减自动更新</small></article></>;
 return <div className="data-chip-list">{species.map(name=><span key={name}>{name}</span>)}</div>;
}
