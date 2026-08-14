"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

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

type Snapshot<T> = { id: string; country: string; data: T; capturedAt: string };
type LogisticsData = { median_days?: number; observed_at?: string; status?: string };
type TradeData = { hs?: string; year?: number; value_usd?: number; status?: string };

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
  const [logistics, setLogistics] = useState<Snapshot<LogisticsData>[]>([]);
  const [trade, setTrade] = useState<Snapshot<TradeData>[]>([]);
  const [countryFilter, setCountryFilter] = useState("ALL");
  const [speciesFilter, setSpeciesFilter] = useState("ALL");
  const [chartCountry, setChartCountry] = useState("KZ");

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const [priceResponse, logisticsResponse, tradeResponse] = await Promise.all([
          fetch(API, { cache: "no-store" }),
          fetch("/api/ingest/snapshot?metric=logistics&latest=1&limit=500", { cache: "no-store" }),
          fetch("/api/ingest/snapshot?metric=trade&latest=1&limit=500", { cache: "no-store" }),
        ]);
        if (!priceResponse.ok) throw new Error(`HTTP ${priceResponse.status}`);
        const [pricePayload, logisticsPayload, tradePayload] = await Promise.all([
          priceResponse.json(), logisticsResponse.ok ? logisticsResponse.json() : { records: [] }, tradeResponse.ok ? tradeResponse.json() : { records: [] },
        ]);
        if (active) { setRows(pricePayload.records ?? []); setLogistics(logisticsPayload.records ?? []); setTrade(tradePayload.records ?? []); setUpdated(new Date()); setError(""); }
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

  const priceTrend = useMemo(() => {
    const byDate = new Map<string, number[]>();
    rows.filter(row => row.country === chartCountry &&
      (speciesFilter === "ALL" || row.species_id === speciesFilter) &&
      Number.isFinite(Number(row.normalized_usd_per_kg))
    ).forEach(row => byDate.set(row.observation_date, [
      ...(byDate.get(row.observation_date) ?? []), Number(row.normalized_usd_per_kg),
    ]));
    return Array.from(byDate.entries()).sort(([a], [b]) => a.localeCompare(b)).slice(-14)
      .map(([date, prices]) => ({ date, value: median(prices) ?? 0, samples: prices.length }));
  }, [rows, chartCountry, speciesFilter]);

  const chartGeometry = useMemo(() => {
    const values = priceTrend.map(point => point.value);
    const min = values.length ? Math.min(...values) : 0;
    const max = values.length ? Math.max(...values) : 0;
    const spread = Math.max(max - min, max * .08, 1);
    const points = priceTrend.map((point, index) => ({
      ...point,
      x: priceTrend.length === 1 ? 50 : 7 + index / (priceTrend.length - 1) * 86,
      y: 84 - (point.value - min) / spread * 66,
    }));
    return { min, max, points };
  }, [priceTrend]);

  const logisticsByCountry = useMemo(() => {
    const result = new Map<string, number>();
    logistics.filter(row => row.data.status === "live" && Number.isFinite(row.data.median_days)).sort((a, b) => (b.data.observed_at ?? b.capturedAt).localeCompare(a.data.observed_at ?? a.capturedAt)).forEach(row => {
      if (!result.has(row.country)) result.set(row.country, Number(row.data.median_days));
    });
    return result;
  }, [logistics]);

  const tradeByCountry = useMemo(() => {
    const latestBySeries = new Map<string, Snapshot<TradeData>>();
    trade.filter(row => row.data.status === "live" && row.data.hs && Number.isFinite(row.data.year) && Number.isFinite(row.data.value_usd)).forEach(row => {
      const key = `${row.country}|${row.data.hs}|${row.data.year}`;
      const previous = latestBySeries.get(key);
      if (!previous || row.capturedAt > previous.capturedAt) latestBySeries.set(key, row);
    });
    const latestYear = new Map<string, number>();
    latestBySeries.forEach(row => latestYear.set(row.country, Math.max(latestYear.get(row.country) ?? 0, Number(row.data.year))));
    const totals = new Map<string, number>();
    latestBySeries.forEach(row => {
      if (Number(row.data.year) === latestYear.get(row.country)) totals.set(row.country, (totals.get(row.country) ?? 0) + Number(row.data.value_usd));
    });
    return totals;
  }, [trade]);

  const tradeTier = useMemo(() => {
    const values = countries.map(([code]) => tradeByCountry.get(code)).filter((value): value is number => value != null).sort((a, b) => a - b);
    return (code: string) => { const value = tradeByCountry.get(code); if (value == null || !values.length) return "thin"; const rank = values.indexOf(value) / Math.max(values.length - 1, 1); return rank >= .67 ? "thick" : rank >= .34 ? "medium" : "thin"; };
  }, [tradeByCountry]);

  const logisticsAverage = useMemo(() => {
    const values = Array.from(logisticsByCountry.values());
    return values.length ? { value: values.reduce((sum, value) => sum + value, 0) / values.length, count: values.length } : null;
  }, [logisticsByCountry]);

  return <main className="live-screen">
    <header className="screen-head">
      <div><span>INHEN CENTRAL ASIA INTELLIGENCE</span><h1>中亚菌类市场实时数据中枢</h1></div>
      <div className="screen-status"><i /> 数据链路在线 · POWER BI READY<br/><small>{updated ? `更新于 ${updated.toLocaleTimeString("zh-CN")}` : "正在连接…"}</small></div>
    </header>

    <div className="screen-quality">
      <span><i />最新数据日 {latestDate || "—"}</span>
      <b>有效价格 {latestRows.length} 条</b>
      <b>国家覆盖 {stats.countries}/5</b>
      <em>gap 统计尚未接入当前只读接口</em>
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
        <div className="screen-title price-chart-title"><span>01</span><div><b>国家市场价格趋势</b><small>MEDIAN PRICE · USD / KG</small></div></div>
        <div className="price-chart-controls" aria-label="趋势图国家筛选">
          {countries.map(([code, name]) => <button className={chartCountry === code ? "active" : ""} onClick={() => setChartCountry(code)} key={code}>{name}<small>{code}</small></button>)}
        </div>
        <div className="market-price-chart">
          <header><div><small>当前市场</small><b>{countries.find(([code]) => code === chartCountry)?.[1]}</b></div><div><small>价格区间</small><b>${chartGeometry.min.toFixed(2)} — ${chartGeometry.max.toFixed(2)}</b></div><div><small>统计口径</small><b>{speciesFilter === "ALL" ? "全部菌种" : speciesOptions.find(([id]) => id === speciesFilter)?.[1]}</b></div></header>
          {chartGeometry.points.length ? <div className="price-chart-canvas">
            <div className="chart-scale"><span>${chartGeometry.max.toFixed(2)}</span><span>${((chartGeometry.max + chartGeometry.min) / 2).toFixed(2)}</span><span>${chartGeometry.min.toFixed(2)}</span></div>
            <svg viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label={`${chartCountry} 市场价格折线图`}>
              <defs><linearGradient id="priceArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#39e39a" stopOpacity=".3"/><stop offset="1" stopColor="#39e39a" stopOpacity="0"/></linearGradient></defs>
              <path className="price-chart-area" d={`M ${chartGeometry.points.map(point => `${point.x} ${point.y}`).join(" L ")} L ${chartGeometry.points.at(-1)?.x} 91 L ${chartGeometry.points[0].x} 91 Z`} />
              <polyline points={chartGeometry.points.map(point => `${point.x},${point.y}`).join(" ")} />
              {chartGeometry.points.map(point => <circle key={point.date} cx={point.x} cy={point.y} r="1.25"><title>{point.date} · ${point.value.toFixed(2)}/kg · {point.samples}条样本</title></circle>)}
            </svg>
            <div className="chart-dates"><span>{chartGeometry.points[0].date}</span><span>{chartGeometry.points.at(-1)?.date}</span></div>
          </div> : <p className="screen-empty">当前国家或菌种暂无可用价格趋势</p>}
          <footer><span>● 每日挂牌价中位数</span><em>最近 {chartGeometry.points.length} 个有效采集日 · 悬停数据点查看样本</em></footer>
        </div>
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
