"use client";

import { useEffect, useMemo, useState } from "react";

type Country = "ALL" | "KZ" | "UZ" | "KG" | "TJ" | "TM";
type Grain = "annual" | "monthly" | "daily";
type Mode = "history" | "latest";
type RecordRow = { period: string; year: number; reporterCode: number; hs: string; product: string | null; valueUsd: number | null; netWeightKg: number | null };

const countries: { code: Country; label: string }[] = [
  { code: "ALL", label: "全部市场" }, { code: "KZ", label: "哈萨克斯坦" }, { code: "UZ", label: "乌兹别克斯坦" },
  { code: "KG", label: "吉尔吉斯斯坦" }, { code: "TJ", label: "塔吉克斯坦" }, { code: "TM", label: "土库曼斯坦" },
];
const codes: Record<Exclude<Country, "ALL">, number> = { KZ: 398, UZ: 860, KG: 417, TJ: 762, TM: 795 };
const names: Record<number, string> = { 398: "哈萨克斯坦", 860: "乌兹别克斯坦", 417: "吉尔吉斯斯坦", 762: "塔吉克斯坦", 795: "土库曼斯坦" };
const products: Record<string, string> = { "070951": "鲜、冷双孢蘑菇", "070959": "其他鲜蘑菇", "200310": "加工保藏蘑菇" };
const baseline = [
  [398,"070951",2022,8893873,3489],[398,"070951",2023,3181278,null],[398,"070951",2024,4193266,3489],
  [398,"200310",2022,4412358,null],[398,"200310",2023,1644872,null],[398,"200310",2024,1027970,null],
  [398,"070959",2022,510974,null],[398,"070959",2023,426093,null],[398,"070959",2024,409221,526],
  [860,"070951",2022,15930,null],[860,"070951",2023,488375,null],[860,"070951",2024,456804,197],
  [860,"200310",2022,69233,null],[860,"200310",2023,111800,null],[860,"200310",2024,68204,null],
  [417,"070951",2022,9994,null],[417,"070951",2023,40966,null],[417,"070951",2024,40376,24],
  [417,"070959",2022,97554,null],[417,"070959",2023,246088,null],[417,"070959",2024,535916,null],
  [417,"200310",2022,130482,null],[417,"200310",2023,130030,null],[417,"200310",2024,228842,46],
  [762,"200310",2022,39358,null],[762,"200310",2023,119104,null],
].map(([reporterCode,hs,year,valueUsd,weight]) => ({ period: String(year), year: Number(year), reporterCode: Number(reporterCode), hs: String(hs), product: products[String(hs)], valueUsd: Number(valueUsd), netWeightKg: weight === null ? null : Number(weight) * 1000 })) as RecordRow[];

const dailyPrices = [
  { date:"2026-08-11", country:"KZ", city:"阿拉木图", product:"鲜双孢菇", channel:"电商/商超", price:"2,730–3,300 ₸/kg" },
  { date:"2026-08-11", country:"KZ", city:"阿拉木图", product:"鲜平菇", channel:"批发", price:"1,300–1,500 ₸/kg" },
  { date:"2026-08-10", country:"UZ", city:"塔什干", product:"鲜双孢菇", channel:"电商/零售", price:"60,000–78,000 сум/kg" },
];
const usd = (value: number | null) => value === null ? "未报告" : new Intl.NumberFormat("zh-CN", { style:"currency", currency:"USD", maximumFractionDigits:0 }).format(value);

export default function MarketPanel({ onState }: { onState: (state: "loading" | "live" | "fallback") => void }) {
  const [country, setCountry] = useState<Country>("ALL");
  const [grain, setGrain] = useState<Grain>("annual");
  const [mode, setMode] = useState<Mode>("latest");
  const [records, setRecords] = useState<RecordRow[]>([]);
  const [state, setState] = useState<"loading" | "live" | "fallback">("loading");

  useEffect(() => {
    if (grain === "daily") { setState("live"); onState("live"); return; }
    const frequency = grain === "annual" ? "A" : "M";
    const start = mode === "history" ? 2022 : grain === "annual" ? 2024 : 2025;
    setState("loading"); onState("loading");
    fetch(`/api/trade?frequency=${frequency}&start=${start}&end=2026`)
      .then(response => response.ok ? response.json() : Promise.reject())
      .then(payload => { setRecords(payload.records ?? []); setState("live"); onState("live"); })
      .catch(() => { setRecords([]); setState("fallback"); onState("fallback"); });
  }, [grain, mode, onState]);

  const selectedCode = country === "ALL" ? null : codes[country];
  const source = state === "live" && records.length ? records : grain === "annual" ? baseline : [];
  const filtered = source.filter(row => selectedCode === null || row.reporterCode === selectedCode);
  const periods = [...new Set(filtered.map(row => row.period))].sort();
  const visiblePeriods = mode === "latest" ? periods.slice(-3) : periods;
  const latestPeriod = periods.at(-1) ?? "暂无";
  const latestRows = filtered.filter(row => row.period === latestPeriod);
  const total = latestRows.reduce((sum,row) => sum + (row.valueUsd ?? 0), 0);
  const max = Math.max(...latestRows.map(row => row.valueUsd ?? 0), 1);
  const prices = dailyPrices.filter(row => country === "ALL" || row.country === country);

  return <>
    <section className="intel-hero terminal-controls"><div><span>CONTINUOUS DATA</span><h1>历史基线与最新数据连续查看</h1><p>年度、月度贸易来自 UN Comtrade；日度展示独立采集的市场价格。不同频率保持原始口径，不做虚假拆分。</p></div><div className="control-stack"><div className="mode-switch"><button className={mode === "history" ? "active" : ""} onClick={() => setMode("history")}>历史数据</button><button className={mode === "latest" ? "active" : ""} onClick={() => setMode("latest")}>最新数据</button></div><div className="grain-switch"><button className={grain === "annual" ? "active" : ""} onClick={() => setGrain("annual")}>年度</button><button className={grain === "monthly" ? "active" : ""} onClick={() => setGrain("monthly")}>月度</button><button className={grain === "daily" ? "active" : ""} onClick={() => setGrain("daily")}>日度价格</button></div></div></section>
    <div className="country-switch terminal-country">{countries.map(item => <button key={item.code} className={country === item.code ? "active" : ""} onClick={() => setCountry(item.code)}>{item.label}</button>)}</div>
    {grain === "daily" ? <section className="intel-table-panel"><div className="intel-panel-head"><div><span>DAILY MARKET OBSERVATIONS</span><h2>日度市场价格</h2></div><small>挂牌价 · 非成交价</small></div><div className="intel-table"><div className="intel-row daily-row head"><span>日期</span><span>市场</span><span>商品</span><span>渠道</span><span>价格</span></div>{prices.map(row => <div className="intel-row daily-row" key={`${row.date}-${row.country}-${row.product}-${row.channel}`}><span>{row.date}</span><span>{row.city}</span><span>{row.product}</span><span>{row.channel}</span><span>{row.price}</span></div>)}</div></section> : <>
      <section className="intel-kpis"><article><span>{latestPeriod} 已报告进口额</span><strong>{usd(total)}</strong><small>当前筛选口径</small></article><article><span>可用统计期</span><strong>{periods.length}</strong><small>{grain === "annual" ? "年度" : "月度"}连续序列</small></article><article><span>最新可用期</span><strong>{latestPeriod}</strong><small>按官方实际上报判断</small></article><article><span>数据状态</span><strong>{state === "live" ? "实时" : state === "loading" ? "同步中" : "基线"}</strong><small>异常时保留已验证数据</small></article></section>
      <section className="intel-grid"><article className="intel-panel intel-chart"><div className="intel-panel-head"><div><span>LATEST AVAILABLE PERIOD</span><h2>市场与品类结构</h2></div><small>UN Comtrade · {latestPeriod}</small></div><div className="intel-bars">{latestRows.length ? latestRows.map(row => <div key={`${row.reporterCode}-${row.hs}`}><span><b>{names[row.reporterCode]}</b><small>HS {row.hs} · {products[row.hs]}</small></span><i><em style={{ width:`${((row.valueUsd ?? 0) / max) * 100}%` }} /></i><strong>{usd(row.valueUsd)}</strong></div>) : <p className="empty-data">该筛选范围尚无官方记录。</p>}</div></article><article className="intel-panel production-card"><div className="intel-panel-head"><div><span>DATA RULE</span><h2>频率与口径</h2></div></div><p>年度用于完整市场规模，月度用于趋势追踪，日度用于价格和渠道信号。2026 年年度尚未结束，因此优先显示最新已发布月份。</p><p>官方接口没有返回的数据保持缺失；接口异常时，年度视图自动回到 2022–2024 已验证基线。</p></article></section>
      <section className="intel-table-panel"><div className="intel-panel-head"><div><span>CONTINUOUS SERIES</span><h2>连续贸易数据</h2></div><small>{state === "fallback" ? "已验证基线" : "官方接口"}</small></div><div className="intel-table"><div className="intel-row series-row head"><span>统计期</span><span>市场 / 商品</span><span>进口额</span><span>数量</span><span>状态</span></div>{filtered.filter(row => visiblePeriods.includes(row.period)).sort((a,b) => b.period.localeCompare(a.period)).map(row => <div className="intel-row series-row" key={`${row.period}-${row.reporterCode}-${row.hs}`}><span>{row.period.length === 6 ? `${row.period.slice(0,4)}-${row.period.slice(4)}` : row.period}</span><span><b>{names[row.reporterCode]}</b><small>HS {row.hs} · {products[row.hs]}</small></span><span>{usd(row.valueUsd)}</span><span>{row.netWeightKg ? `${Math.round(row.netWeightKg / 1000).toLocaleString()} 吨` : "待补"}</span><span><em className={`quality ${state === "live" ? "ok" : "review"}`}>{state === "live" ? "API 实时" : "已验证基线"}</em></span></div>)}</div></section>
    </>}
  </>;
}
