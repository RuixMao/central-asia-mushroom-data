"use client";

import { useEffect, useMemo, useState } from "react";
import { mirrorRecords } from "../../data";
import { countryNames, latestByCountry, loadLivePrices, marketCodesFromRows, marketName, rowPrice, speciesLabel, type LivePriceRow } from "../../market-display";

const money = (value: number) => value ? `$${value.toLocaleString("en-US")}` : "暂无贸易额";
const readExpand = () => typeof window === "undefined" ? null : (new URL(window.location.href).searchParams.get("expand")?.toUpperCase() ?? null);

export default function CountryAccordion() {
  const [expanded, setExpanded] = useState<string | null>(readExpand);
  const [rows, setRows] = useState<LivePriceRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const syncExpandedCountry = () => setExpanded(readExpand());
    window.addEventListener("popstate", syncExpandedCountry);
    loadLivePrices().then(setRows).catch(() => setRows([])).finally(() => setLoading(false));
    return () => window.removeEventListener("popstate", syncExpandedCountry);
  }, []);

  const latest = useMemo(() => latestByCountry(rows), [rows]);
  const marketCodes=useMemo(()=>marketCodesFromRows(rows),[rows]);
  const toggle = (code: string) => {
    const next = expanded === code ? null : code;
    setExpanded(next);
    const url = new URL(window.location.href);
    if (next) url.searchParams.set("expand", next);
    else url.searchParams.delete("expand");
    window.history.pushState({}, "", `${url.pathname}${url.search}`);
  };

  return <section className="country-accordion" aria-label="目标市场列表">{marketCodes.map((code) => {
    const trade = mirrorRecords.filter((row) => row.countryCode === code);
    const total = trade.reduce((sum, row) => sum + Number(row.importerCifUsd ?? row.confirmedTradeUsd ?? 0), 0);
    const tradeYears=Array.from(new Set(trade.map(row=>row.year).filter(Boolean))).sort();
    const prices = latest.filter((row) => row.country === code);
    const channels = new Set(prices.map((row) => row.platform_name)).size;
    const date = prices.reduce((current, row) => row.observation_date > current ? row.observation_date : current, "");
    const open = expanded === code;
    return <article className={open ? "open" : ""} key={code}>
      <button type="button" onClick={() => toggle(code)} aria-expanded={open}><span>{code}</span><b>{prices[0]?marketName(prices[0]):countryNames[code]??code}</b><em>{prices.length ? `已有 ${prices.length} 条价格` : trade.length ? "已有贸易数据" : "市场信息"}</em><i aria-hidden="true">{open ? "−" : "＋"}</i></button>
      <div className="country-inline-panel" aria-hidden={!open}>
        <div><span>所列 HS 进口额</span><strong>{trade.length ? `${money(total)} · ${tradeYears.join("/")}` : "查看国家信息"}</strong></div>
        <div><span>公开价格</span><strong>{prices[0] ? rowPrice(prices[0]) : loading ? "正在加载" : "暂无公开价格"}</strong></div>
        <div><span>渠道覆盖</span><strong>{channels || "暂无渠道记录"}</strong></div>
        <div><span>更新时间</span><strong>{date || "随市场信息更新"}</strong></div>
        <div><span>下一步</span><strong>{prices.length ? "查看价格、贸易与风险" : "查看已有市场信息"}</strong></div>
        {prices.length > 0 && <p>已覆盖品种：{Array.from(new Set(prices.slice(0, 3).map((row) => speciesLabel(row.species_id)))).join("、")}</p>}
        <a href={`/markets/${code}`} data-native-navigation="true">进入国家工作台 →</a>
      </div>
    </article>;
  })}</section>;
}
