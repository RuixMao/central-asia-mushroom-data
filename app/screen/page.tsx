"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { mirrorRecords } from "../data";

type PriceRow = {
  observation_date: string;
  observed_at: string;
  product_id: string;
  country: string;
  country_name?: string;
  city: string;
  species_id: string;
  species_name?: string;
  product_form: string;
  platform_name: string;
  original_title: string;
  normalized_usd_per_kg: number | null;
};

const API = "/api/powerbi?table=prices";
const countries = [
  ["KZ", "哈萨克斯坦", "阿拉木图"], ["UZ", "乌兹别克斯坦", "塔什干"],
  ["KG", "吉尔吉斯斯坦", "比什凯克"], ["TJ", "塔吉克斯坦", "杜尚别"],
  ["TM", "土库曼斯坦", "阿什哈巴德"],
];

const median = (values: number[]) => {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
};

export default function ScreenPage() {
  const [rows, setRows] = useState<PriceRow[]>([]);
  const [updated, setUpdated] = useState<Date | null>(null);
  const [error, setError] = useState("");
  const [countryFilter, setCountryFilter] = useState("ALL");
  const [speciesFilter, setSpeciesFilter] = useState("ALL");

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const priceResponse = await fetch(API, { cache: "no-store" });
        if (!priceResponse.ok) throw new Error(`HTTP ${priceResponse.status}`);
        const pricePayload = await priceResponse.json();
        if (active) { setRows(pricePayload.records ?? []); setUpdated(new Date()); setError(""); }
      } catch (reason) {
        if (active) setError(reason instanceof Error ? reason.message : "数据连接失败");
      }
    };
    load();
    const timer = window.setInterval(load, 60_000);
    return () => { active = false; window.clearInterval(timer); };
  }, []);

  const speciesOptions = useMemo(() => Array.from(new Map(rows.map(row => [row.species_id, row.species_name ?? row.species_id])).entries()), [rows]);
  const latestDate = useMemo(() => rows.reduce((latest, row) => row.observation_date > latest ? row.observation_date : latest, ""), [rows]);
  const latestRows = useMemo(() => rows.filter(row => row.observation_date === latestDate), [rows, latestDate]);
  const validPrices = useMemo(() => rows.map(row => Number(row.normalized_usd_per_kg)).filter(Number.isFinite), [rows]);
  const priceRange = useMemo(() => validPrices.length ? [Math.min(...validPrices), Math.max(...validPrices)] : [0, 0], [validPrices]);

  const filteredRows = useMemo(() => rows.filter(row =>
    (countryFilter === "ALL" || row.country === countryFilter) &&
    (speciesFilter === "ALL" || row.species_id === speciesFilter)
  ), [rows, countryFilter, speciesFilter]);

  const stats = useMemo(() => ({
    countries: new Set(rows.map(row => row.country)).size,
    species: new Set(rows.map(row => row.species_id)).size,
    platforms: new Set(rows.map(row => row.platform_name)).size,
  }), [rows]);

  const countryGroups = useMemo(() => countries
    .filter(([code]) => countryFilter === "ALL" || countryFilter === code)
    .map(([code, name]) => {
      const countryRows = filteredRows.filter(row => row.country === code);
      const countryMedian = median(countryRows.map(row => Number(row.normalized_usd_per_kg)).filter(Number.isFinite));
      const speciesGroups = Array.from(new Set(countryRows.map(row => row.species_id))).map(speciesId => {
        const speciesRows = countryRows.filter(row => row.species_id === speciesId);
        const byProduct = new Map<string, PriceRow[]>();
        speciesRows.forEach(row => byProduct.set(row.product_id, [...(byProduct.get(row.product_id) ?? []), row]));
        const products = Array.from(byProduct.entries()).map(([productId, history]) => ({
          productId,
          history: history.sort((a, b) => a.observation_date.localeCompare(b.observation_date)).slice(-7),
          latest: history.sort((a, b) => b.observation_date.localeCompare(a.observation_date))[0],
        }));
        return { speciesId, name: speciesRows[0]?.species_name ?? speciesId, products };
      });
      return { code, name, rows: countryRows, countryMedian, speciesGroups };
    }), [filteredRows, countryFilter]);

  const tradeOverview = useMemo(() => {
    const countryData = countries.map(([code, name]) => {
      const items = mirrorRecords.filter(record => record.countryCode === code);
      const total = items.reduce((sum, item) => sum + Number(item.importerCifUsd ?? item.confirmedTradeUsd ?? 0), 0);
      const china = items.reduce((sum, item) => sum + Number(item.chinaFobUsd ?? 0), 0);
      const grade = items.some(item => item.confidence === "B" || item.confidence === "B+") ? "B+" : "A+";
      return { code, name, items, total, china, grade, share: total > 0 ? china / total * 100 : null };
    });
    const total = countryData.reduce((sum, country) => sum + country.total, 0);
    const china = countryData.reduce((sum, country) => sum + country.china, 0);
    return { countries: countryData, total, china, share: total > 0 ? china / total * 100 : null };
  }, []);

  return <main className="live-screen">
    <header className="screen-head">
      <div><span>INHEN CENTRAL ASIA INTELLIGENCE</span><h1>中亚菌类市场实时数据中枢</h1></div>
      <div className="screen-status"><i /> 数据链路在线 · POWER BI READY<br/><small>{updated ? `更新于 ${updated.toLocaleTimeString("zh-CN")}` : "正在连接…"}</small></div>
    </header>

    <div className="screen-quality">
      <span><i />最新数据日 {latestDate || "—"}</span>
      <b>有效价格 {latestRows.length} 条</b>
      <b>国家覆盖 {stats.countries}/5</b>
      <strong>挂牌价 ≠ 成交价，仅供趋势参考</strong>
    </div>

    <section className="screen-kpis">
      <article><span>有效价格记录</span><b>{rows.length}</b><small>历史有效观察</small></article>
      <article><span>国家覆盖</span><b>{stats.countries}<em>/5</em></b><small>中亚五国</small></article>
      <article><span>菌种覆盖</span><b>{stats.species}</b><small>{speciesOptions.map(([, name]) => name).join("、") || "—"}</small></article>
      <article><span>渠道覆盖</span><b>{stats.platforms}</b><small>公开零售渠道</small></article>
      <article className="range-kpi"><span>挂牌价格范围</span><b>${priceRange[0].toFixed(2)}—${priceRange[1].toFixed(2)}</b><small>USD/kg · 含不同规格包装折算</small></article>
    </section>

    <nav className="screen-filters" aria-label="数据筛选">
      <div><span>国家</span><button className={countryFilter === "ALL" ? "active" : ""} onClick={() => setCountryFilter("ALL")}>全部</button>{countries.map(([code, name]) => <button className={countryFilter === code ? "active" : ""} onClick={() => setCountryFilter(code)} key={code}>{name}</button>)}</div>
      <div><span>菌种</span><button className={speciesFilter === "ALL" ? "active" : ""} onClick={() => setSpeciesFilter("ALL")}>全部</button>{speciesOptions.map(([id, name]) => <button className={speciesFilter === id ? "active" : ""} onClick={() => setSpeciesFilter(id)} key={id}>{name}</button>)}</div>
    </nav>

    <section className="screen-grid">
      <article className="screen-map">
        <div className="screen-title price-chart-title"><span>01</span><div><b>中亚五国菌类贸易与可信度</b><small>COUNTRY → HS CATEGORY → DATA GRADE</small></div></div>
        <div className="screen-trade-summary">
          <div className={`screen-share-ring ${tradeOverview.share == null ? "empty" : ""}`} style={tradeOverview.share == null ? undefined : { background: `conic-gradient(#42e6b0 0 ${tradeOverview.share}%, #1b4d68 ${tradeOverview.share}% 100%)` }}><div><strong>{tradeOverview.share?.toFixed(1) ?? "—"}%</strong><span>中国金额占比</span></div></div>
          <div><span>2024 已确认贸易规模</span><strong>${(tradeOverview.total / 1_000_000).toFixed(2)}M</strong><small>覆盖中亚五国 · 8 个国家与品类组合</small></div>
        </div>
        <div className="screen-trade-countries">{tradeOverview.countries.map(country => <article key={country.code}>
          <header><div><b>{country.name}</b><small>{country.code} · {country.items.length} 个品类</small></div><em className={`screen-grade grade-${country.grade.replace("+", "plus")}`}>{country.grade}</em></header>
          <div className="screen-country-total"><span>已确认金额</span><b>${country.total.toLocaleString("en-US")}</b><small>{country.share == null ? "—" : `其中中国占 ${country.share.toFixed(1)}%`}</small></div>
          <div className="screen-hs-list">{country.items.map(item => <div key={item.hs}><span><b>{item.product}</b><small>HS {item.hs}</small></span><strong>${Number(item.importerCifUsd ?? item.confirmedTradeUsd ?? 0).toLocaleString("en-US")}</strong><em>{item.confidence}</em></div>)}</div>
          <p>{country.items[0]?.confidenceBasis}</p>
        </article>)}</div>
        <p className="trade-method">评级说明：A+ 为进口国公布金额、数量和来源国；A 为可靠的双向申报；B+ 为两个或以上伙伴国申报汇总；B 为单一可靠伙伴国申报。金额均为 2024 年美元值。</p>
      </article>

      <article className="screen-feed">
        <div className="screen-title"><span>02</span><div><b>国家与菌种价格观察</b><small>COUNTRY → SPECIES → SKU</small></div></div>
        {error && <p className="screen-error">数据连接异常：{error}</p>}
        <div className="country-price-groups">
          {countryGroups.map(group => <section className={`country-price-group ${group.rows.length ? "has-data" : ""}`} key={group.code}>
            <header><div><b>{group.name}</b><small>{group.code}</small></div><em>{group.rows.length} 条 · {group.speciesGroups.length} 菌种</em></header>
            {group.speciesGroups.length ? <div className="species-price-groups">{group.speciesGroups.map(speciesGroup => <article key={speciesGroup.speciesId}>
              <div className="species-group-head"><b>{speciesGroup.name}</b><span>{speciesGroup.products.length} SKU</span></div>
              {speciesGroup.products.slice(0, 5).map(({ productId, latest, history }) => {
                const price = Number(latest.normalized_usd_per_kg);
                const previous = history.length > 1 ? Number(history[history.length - 2].normalized_usd_per_kg) : null;
                const tone = group.countryMedian == null ? "" : price <= group.countryMedian ? "price-low" : "price-high";
                const max = Math.max(...history.map(item => Number(item.normalized_usd_per_kg)).filter(Number.isFinite), 1);
                return <div className="species-price-row" key={productId}>
                  <span title={latest.original_title}>{latest.city} · {latest.platform_name}<small>{latest.observation_date}</small></span>
                  <span className="mini-trend" aria-label="近七次价格趋势">{history.map((item, index) => <i key={`${item.observation_date}-${index}`} style={{height: `${Math.max(18, Number(item.normalized_usd_per_kg) / max * 100)}%`}} />)}</span>
                  <em className={tone}>${price.toFixed(2)}{previous != null && previous !== price && <b>{price > previous ? "↑" : "↓"}</b>}<small>USD / 公斤</small></em>
                </div>;
              })}
            </article>)}</div> : <p className="country-collecting">当前筛选下暂无有效价格</p>}
          </section>)}
          {!rows.length && !error && <p className="screen-empty">等待五国自动化采集写入数据…</p>}
        </div>
      </article>
    </section>

    <footer className="screen-footer"><span>数据源：Cloudflare D1 · 每 60 秒自动刷新 · 数据版本 {latestDate || "—"}</span><Link href="/">返回因恒科技主页</Link><a href={API} target="_blank" rel="noreferrer">Power BI 数据接口 →</a></footer>
  </main>;
}
