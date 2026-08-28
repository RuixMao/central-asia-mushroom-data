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
  normalized_quantity_kg?: number | null;
  current_price?: number | null;
  promotion_price?: number | null;
  in_stock?: boolean | null;
};

type DailyRow = { date: string; country: string; speciesId: string; validSkuCount: number; inStockSkuCount: number; outOfStockRate: number; promotionShare: number; qualityGrade?: string; sevenDayChange?: number | null };

type Snapshot<T> = { id: string; country: string; data: T; capturedAt: string };
type TradeData = { hs?: string; year?: number; value_usd?: number; partner_value_usd?: number; partner_code?: string | number; status?: string; reporting_basis?: string; estimate_lower_usd?: number; estimate_upper_usd?: number; coverage_pct?: number; confidence?: string; source_id?: string; source_role?: string; availability?: string };
const API = "/api/powerbi?table=prices";
const roles = [
  ["buyer", "采购与渠道", "比价、规格、库存"], ["supplier", "供应与生产", "价格机会、贸易空间"],
  ["investor", "投资与决策", "规模、趋势、集中度"], ["researcher", "研究与分析", "来源、口径、可信度"],
] as const;
type Role = typeof roles[number][0];
const countries = [
  ["KZ", "哈萨克斯坦", "阿拉木图"], ["UZ", "乌兹别克斯坦", "塔什干"],
  ["KG", "吉尔吉斯斯坦", "比什凯克"], ["TJ", "塔吉克斯坦", "杜尚别"],
  ["TM", "土库曼斯坦", "阿什哈巴德"],
  ["LA", "老挝", "万象"], ["VN", "越南", "胡志明市"],
  ["TH", "泰国", "曼谷"], ["MM", "缅甸", "仰光"], ["KH", "柬埔寨", "金边"],
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
  const [trade, setTrade] = useState<Snapshot<TradeData>[]>([]);
  const [daily, setDaily] = useState<DailyRow[]>([]);
  const [countryFilter, setCountryFilter] = useState("ALL");
  const [speciesFilter, setSpeciesFilter] = useState("ALL");
  const [role, setRole] = useState<Role>("researcher");
  const [comparableOnly, setComparableOnly] = useState(false);

  useEffect(() => {
    const queryRole = new URLSearchParams(window.location.search).get("role") as Role | null;
    const savedRole = window.localStorage.getItem("screen-role") as Role | null;
    const valid = roles.map(item => item[0]);
    setRole(valid.includes(queryRole as Role) ? queryRole! : valid.includes(savedRole as Role) ? savedRole! : "researcher");
  }, []);

  const chooseRole = (nextRole: Role) => {
    setRole(nextRole);
    window.localStorage.setItem("screen-role", nextRole);
    const url = new URL(window.location.href);
    url.searchParams.set("role", nextRole);
    window.history.replaceState({}, "", url);
  };

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const [priceResponse, tradeResponse, dailyResponse] = await Promise.all([
          fetch(API, { cache: "no-store" }),
          fetch("/api/ingest/snapshot?metric=trade&limit=2000", { cache: "no-store" }),
          fetch("/api/powerbi?table=daily", { cache: "no-store" }),
        ]);
        if (!priceResponse.ok) throw new Error(`HTTP ${priceResponse.status}`);
        const [pricePayload, tradePayload, dailyPayload] = await Promise.all([
          priceResponse.json(), tradeResponse.ok ? tradeResponse.json() : { records: [] }, dailyResponse.ok ? dailyResponse.json() : { records: [] },
        ]);
        if (active) { setRows(pricePayload.records ?? []); setTrade(tradePayload.records ?? []); setDaily(dailyPayload.records ?? []); setUpdated(new Date()); setError(""); }
      } catch {
        if (active) setError("部分数据暂时未能更新，请稍后查看");
      }
    };
    load();
    const timer = window.setInterval(load, 60_000);
    return () => { active = false; window.clearInterval(timer); };
  }, []);

  const speciesOptions = useMemo(() => Array.from(new Map(rows.map(row => [row.species_id, row.species_name ?? row.species_id])).entries()), [rows]);
  const latestDate = useMemo(() => rows.reduce((latest, row) => row.observation_date > latest ? row.observation_date : latest, ""), [rows]);
  const latestRows = useMemo(() => rows.filter(row => row.observation_date === latestDate), [rows, latestDate]);
  const dominantQuantity = useMemo(() => {
    const counts = new Map<number, number>();
    latestRows.forEach(row => { const quantity = Number(row.normalized_quantity_kg); if (quantity > 0) counts.set(quantity, (counts.get(quantity) ?? 0) + 1); });
    return Array.from(counts.entries()).sort((a, b) => b[1] - a[1])[0]?.[0] ?? null;
  }, [latestRows]);
  const scopedRows = useMemo(() => comparableOnly && dominantQuantity != null ? rows.filter(row => Number(row.normalized_quantity_kg) === dominantQuantity) : rows, [rows, comparableOnly, dominantQuantity]);
  const validPrices = useMemo(() => scopedRows.map(row => Number(row.normalized_usd_per_kg)).filter(Number.isFinite), [scopedRows]);
  const priceRange = useMemo(() => validPrices.length ? [Math.min(...validPrices), Math.max(...validPrices)] : [0, 0], [validPrices]);

  const filteredRows = useMemo(() => scopedRows.filter(row =>
    (countryFilter === "ALL" || row.country === countryFilter) &&
    (speciesFilter === "ALL" || row.species_id === speciesFilter)
  ), [scopedRows, countryFilter, speciesFilter]);

  const stats = useMemo(() => ({
    countries: new Set(latestRows.map(row => row.country)).size,
    species: new Set(rows.map(row => row.species_id)).size,
    platforms: new Set(rows.map(row => row.platform_name)).size,
  }), [rows, latestRows]);

  const countryGroups = useMemo(() => countries
    .filter(([code]) => countryFilter === "ALL" || countryFilter === code)
    .map(([code, name]) => {
      const countryRows = filteredRows.filter(row => row.country === code && row.observation_date === latestDate);
      const countryMedian = median(countryRows.map(row => Number(row.normalized_usd_per_kg)).filter(Number.isFinite));
      const speciesGroups = Array.from(new Set(countryRows.map(row => row.species_id))).map(speciesId => {
        const speciesRows = countryRows.filter(row => row.species_id === speciesId);
        const byProduct = new Map<string, PriceRow[]>();
        speciesRows.forEach(row => byProduct.set(row.product_id, [...(byProduct.get(row.product_id) ?? []), row]));
        const products = Array.from(byProduct.entries()).map(([productId, history]) => ({
          productId,
          history: history.sort((a, b) => a.observation_date.localeCompare(b.observation_date)).slice(-7),
          latest: history.sort((a, b) => b.observation_date.localeCompare(a.observation_date))[0],
        })).sort((a, b) => Number(a.latest.normalized_usd_per_kg) - Number(b.latest.normalized_usd_per_kg));
        return { speciesId, name: speciesRows[0]?.species_name ?? speciesId, products };
      });
      return { code, name, rows: countryRows, countryMedian, speciesGroups };
    }), [filteredRows, countryFilter, latestDate]);

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
  const verifiedTradeSources = useMemo(() => {
    const latest = new Map<string, Snapshot<TradeData>>();
    trade.filter(row => String(row.data.partner_code) === "SOURCE_REGISTRY" && row.data.source_id).forEach(row => {
      const key = `${row.country}|${row.data.source_id}`;
      if (!latest.has(key) || row.capturedAt > latest.get(key)!.capturedAt) latest.set(key, row);
    });
    return Array.from(latest.values()).filter(row => row.data.status === "live" && ["reachable", "configured"].includes(row.data.availability ?? ""));
  }, [trade]);

  const qualitySummary = useMemo(() => {
    const latestDailyDate = daily.reduce((latest, row) => row.date > latest ? row.date : latest, "");
    const current = daily.filter(row => row.date === latestDailyDate);
    const valid = current.reduce((sum, row) => sum + Number(row.validSkuCount ?? 0), 0);
    const inStock = current.reduce((sum, row) => sum + Number(row.inStockSkuCount ?? 0), 0);
    const grades = current.map(row => row.qualityGrade).filter(Boolean) as string[];
    return { date: latestDailyDate, valid, stockRate: valid ? inStock / valid * 100 : null, grade: grades.length ? grades.sort()[Math.floor(grades.length / 2)] : "—" };
  }, [daily]);

  const marketSignals = useMemo(() => {
    const latest = rows.filter(row => row.observation_date === latestDate && Number.isFinite(Number(row.normalized_usd_per_kg)));
    const groups = new Map<string, PriceRow[]>();
    latest.forEach(row => groups.set(row.species_id, [...(groups.get(row.species_id) ?? []), row]));
    return Array.from(groups.entries()).map(([speciesId, items]) => {
      const ordered = [...items].sort((a, b) => Number(a.normalized_usd_per_kg) - Number(b.normalized_usd_per_kg));
      const middle = median(items.map(item => Number(item.normalized_usd_per_kg))) ?? 0;
      const low = ordered[0], high = ordered.at(-1)!;
      return { speciesId, name: low.species_name ?? speciesId, low, high, discount: middle ? (middle - Number(low.normalized_usd_per_kg)) / middle * 100 : 0 };
    });
  }, [rows, latestDate]);

  const tradeTrend = useMemo(() => {
    const latest = new Map<string, Snapshot<TradeData>>();
    trade.filter(row => row.data.hs && Number.isFinite(Number(row.data.year)) && ["ALL", "0"].includes(String(row.data.partner_code ?? "ALL")) && row.data.status === "live").forEach(row => {
      const key = `${row.country}|${row.data.hs}|${row.data.year}`;
      if (!latest.has(key) || row.capturedAt > latest.get(key)!.capturedAt) latest.set(key, row);
    });
    const byYear = new Map<number, number>();
    latest.forEach(row => byYear.set(Number(row.data.year), (byYear.get(Number(row.data.year)) ?? 0) + Number(row.data.value_usd ?? 0)));
    return Array.from(byYear.entries()).sort(([a], [b]) => a - b).slice(-7).map(([year, value]) => ({ year, value }));
  }, [trade]);

  const roleCopy = roles.find(item => item[0] === role)!;
  const formatQuantity = (quantity?: number | null) => quantity == null || !Number.isFinite(Number(quantity)) ? "规格待核" : Number(quantity) >= 1 ? `${Number(quantity).toFixed(Number(quantity) % 1 ? 1 : 0)}kg 装` : `${Math.round(Number(quantity) * 1000)}g 装`;

  return <main className={`live-screen role-${role}`}>
    <header className="screen-head">
      <div><span>INHEN GLOBAL MARKET INTELLIGENCE</span><h1>食用菌出海市场实时数据中枢</h1></div>
      <div className="screen-status"><i /> 数据持续更新<br/><small>{updated ? `本页更新于 ${updated.toLocaleTimeString("zh-CN")}` : "正在获取最新数据"}</small></div>
    </header>

    <nav className="screen-roles" aria-label="选择看板角色">
      <div><small>当前视角</small><b>{roleCopy[1]}</b><span>{roleCopy[2]}</span></div>
      {roles.map(([id, name, description]) => <button key={id} className={role === id ? "active" : ""} onClick={() => chooseRole(id)} aria-pressed={role === id}><b>{name}</b><small>{description}</small></button>)}
    </nav>

    <div className="screen-quality">
      <span><i />最新数据日 {latestDate || "—"}</span>
      <b>有效价格 {latestRows.length} 条</b>
      <b>国家覆盖 {stats.countries}/10（今日）</b>
      <em>数据评级 {qualitySummary.grade} · 在库率 {qualitySummary.stockRate == null ? "—" : `${qualitySummary.stockRate.toFixed(0)}%`} · 核验来源 {verifiedTradeSources.length} 项</em>
      <strong>市场挂牌参考价，不代表最终成交价</strong>
    </div>

    <section className="screen-kpis">
      <article><span>有效价格记录</span><b>{rows.length}</b><small>已纳入分析的价格样本</small></article>
      <article><span>国家覆盖</span><b>{stats.countries}<em>/10（今日）</em></b><small>{countries.filter(([code])=>!latestRows.some(row=>row.country===code)).map(([,name])=>name).join("、")||"全部目标市场"}{stats.countries<10?"今日无有效价格":"今日均有有效价格"}</small></article>
      <article><span>菌种覆盖</span><b>{stats.species}</b><small>{speciesOptions.map(([, name]) => name).join("、") || "—"}</small></article>
      <article><span>渠道覆盖</span><b>{stats.platforms}</b><small>可核验市场渠道</small></article>
      <article className="range-kpi"><span>{comparableOnly ? "同规格价格范围" : "挂牌价格范围"}</span><b>${priceRange[0].toFixed(2)}—${priceRange[1].toFixed(2)}</b><small>USD/kg · {comparableOnly && dominantQuantity != null ? formatQuantity(dominantQuantity) : "已逐行标注包装规格"}</small></article>
    </section>

    <section className={`role-insights role-${role}`}>
      <header><span>关键市场信号</span><b>{roleCopy[1]}视角</b></header>
      {role === "buyer" && marketSignals.slice(0, 3).map(signal => <article key={signal.speciesId}><small>{signal.name}价格洼地</small><b>{signal.low.country_name ?? signal.low.country} · ${Number(signal.low.normalized_usd_per_kg).toFixed(2)}/kg</b><span>{formatQuantity(signal.low.normalized_quantity_kg)} · 较中位价低 {signal.discount.toFixed(0)}%</span></article>)}
      {role === "supplier" && marketSignals.slice(0, 3).map(signal => <article key={signal.speciesId}><small>{signal.name}高价市场</small><b>{signal.high.country_name ?? signal.high.country} · ${Number(signal.high.normalized_usd_per_kg).toFixed(2)}/kg</b><span>提示潜在供给空间，建议结合贸易规模综合判断</span></article>)}
      {role === "investor" && <><article><small>贸易市场规模</small><b>{tradeOverview.total ? `$${(tradeOverview.total / 1_000_000).toFixed(2)}M` : "—"}</b><span>贸易统计与零售挂牌价格分别计算</span></article><article><small>中国来源占比</small><b>{tradeOverview.share == null ? "—" : `${tradeOverview.share.toFixed(1)}%`}</b><span>估算数据均配有可信度标识</span></article><article><small>综合数据评级</small><b>{qualitySummary.grade}</b><span>已核验 {verifiedTradeSources.length} 项数据来源</span></article></>}
      {role === "researcher" && <><article><small>价格样本</small><b>{rows.length} 条</b><span>最新数据日 {latestDate || "—"}</span></article><article><small>市场观察</small><b>{daily.length} 组</b><span>综合数据评级 {qualitySummary.grade}</span></article><article><small>来源透明度</small><b>{verifiedTradeSources.length} 项</b><span>贸易数据来源已核验并保留统计口径</span></article></>}
    </section>

    <nav className="screen-filters" aria-label="数据筛选">
      <div><span>国家</span><button className={countryFilter === "ALL" ? "active" : ""} onClick={() => setCountryFilter("ALL")}>全部</button>{countries.map(([code, name]) => <button className={countryFilter === code ? "active" : ""} onClick={() => setCountryFilter(code)} key={code}>{name}</button>)}</div>
      <div><span>菌种</span><button className={speciesFilter === "ALL" ? "active" : ""} onClick={() => setSpeciesFilter("ALL")}>全部</button>{speciesOptions.map(([id, name]) => <button className={speciesFilter === id ? "active" : ""} onClick={() => setSpeciesFilter(id)} key={id}>{name}</button>)}</div>
      <div><span>规格</span><button className={comparableOnly ? "active" : ""} onClick={() => setComparableOnly(value => !value)} disabled={dominantQuantity == null}>{comparableOnly ? `仅比较 ${formatQuantity(dominantQuantity)}` : "全部规格"}</button><small>同规格模式采用当日样本最多的包装规格，避免跨包装误判。</small></div>
    </nav>

    <section className="screen-grid">
      <article className="screen-map">
        <div className="screen-title price-chart-title"><span>01</span><div><b>目标市场菌类贸易与可信度</b><small>COUNTRY → HS CATEGORY → DATA GRADE</small></div></div>
        <div className="screen-trade-summary">
          <div className={`screen-share-ring ${tradeOverview.share == null ? "empty" : ""}`} style={tradeOverview.share == null ? undefined : { background: `conic-gradient(#42e6b0 0 ${tradeOverview.share}%, #1b4d68 ${tradeOverview.share}% 100%)` }}><div><strong>{tradeOverview.share?.toFixed(1) ?? "—"}%</strong><span>中国金额占比</span></div></div>
          <div><span>2024 已确认贸易规模</span><strong>{tradeOverview.total?`$${(tradeOverview.total / 1_000_000).toFixed(2)}M`:"—"}</strong><small>来源：UN Comtrade 2024 进口数据及伙伴国镜像记录，HS 070951/070959/200310</small></div>
        </div>
        {(role === "supplier" || role === "investor") && tradeTrend.length > 1 && <div className="trade-history">
          <header><b>食用菌进口年度序列</b><small>贸易口径 · USD</small></header>
          <div>{tradeTrend.map(point => { const max = Math.max(...tradeTrend.map(item => item.value), 1); return <span key={point.year}><i style={{height: `${Math.max(8, point.value / max * 100)}%`}} /><b>{point.year}</b><small>${(point.value / 1_000_000).toFixed(1)}M</small></span>; })}</div>
        </div>}
        <p className="screen-source-note">中国金额占比 = 目标市场自中国进口 / 自全球进口；缺少来源国分项的记录不推算占比。</p>
        <div className="screen-trade-countries">{tradeOverview.countries.map(country => <article key={country.code}>
          <header><div><b>{country.name}</b><small>{country.code} · {country.items.length} 个品类</small></div><div><em className={`screen-grade grade-${country.grade.replace("+", "plus")}`}>{country.grade}</em><small className={latestRows.some(row=>row.country===country.code)?"today-ok":"today-gap"}>{latestRows.some(row=>row.country===country.code)?"今日有价格":"今日无有效价格"}</small></div></header>
          <div className="screen-country-total"><span>已确认金额</span><b>${country.total.toLocaleString("en-US")}</b><small>{country.share == null ? "—" : `其中中国占 ${country.share.toFixed(1)}%`}</small></div>
          <div className="screen-hs-list">{country.items.map(item => <div key={item.hs}><span><b>{item.product}</b><small>HS {item.hs}</small></span><strong>${Number(item.importerCifUsd ?? item.confirmedTradeUsd ?? 0).toLocaleString("en-US")}</strong><em>{item.confidence}</em></div>)}</div>
          <p>{country.items[0]?.confidenceBasis}</p>
        </article>)}</div>
        <p className="trade-method">评级说明：A+ 为进口国公布金额、数量和来源国；A 为可靠的双向申报；B+ 为两个或以上伙伴国申报汇总；B 为单一可靠伙伴国申报。金额均为 2024 年美元值。优先采用进口国申报，缺失时采用中国及主要伙伴国出口镜像；已核验来源关系 {verifiedTradeSources.length} 个。</p>
      </article>

      <article className="screen-feed">
        <div className="screen-title"><span>02</span><div><b>国家与菌种价格观察</b><small>COUNTRY → SPECIES → SKU</small></div></div>
        {error && <p className="screen-error">{error}</p>}
        <div className="country-price-groups">
          {countryGroups.map(group => <section className={`country-price-group ${group.rows.length ? "has-data" : ""}`} key={group.code}>
            <header><div><b>{group.name}</b><small>{group.code}</small></div><em>{group.rows.length} 条 · {group.speciesGroups.length} 菌种</em></header>
            {group.speciesGroups.length ? <div className="species-price-groups">{group.speciesGroups.map(speciesGroup => <article key={speciesGroup.speciesId}>
              <div className="species-group-head"><b>{speciesGroup.name}</b><span>{speciesGroup.products.length} SKU</span></div>
              {speciesGroup.products.slice(0, 5).map(({ productId, latest, history }, productIndex) => {
                const price = Number(latest.normalized_usd_per_kg);
                const previous = history.length > 1 ? Number(history[history.length - 2].normalized_usd_per_kg) : null;
                const tone = group.countryMedian == null ? "" : price <= group.countryMedian ? "price-low" : "price-high";
                const max = Math.max(...history.map(item => Number(item.normalized_usd_per_kg)).filter(Number.isFinite), 1);
                return <div className="species-price-row" key={productId}>
                  <span title={latest.original_title}>{latest.city} · {latest.platform_name}<small>{formatQuantity(latest.normalized_quantity_kg)} · {latest.in_stock === false ? "缺货" : "在库"}{latest.promotion_price != null ? " · 促销" : ""}</small></span>
                  <span className="mini-trend" aria-label="近七次价格趋势">{history.map((item, index) => <i key={`${item.observation_date}-${index}`} style={{height: `${Math.max(18, Number(item.normalized_usd_per_kg) / max * 100)}%`}} />)}</span>
                  <em className={tone}>${price.toFixed(2)}{previous != null && previous !== price && <b>{price > previous ? "↑" : "↓"}</b>}<small>USD / 公斤 {productIndex === 0 ? "· 洼地" : productIndex === speciesGroup.products.length - 1 ? "· 高位" : ""}</small></em>
                </div>;
              })}
            </article>)}</div> : <p className="country-collecting">今日暂无可核验价格，历史数据仍可用于趋势参考</p>}
          </section>)}
          {!rows.length && !error && <p className="screen-empty">正在获取目标市场最新数据…</p>}
        </div>
      </article>
    </section>

    <footer className="screen-footer"><span>公开市场与贸易统计资料 · 页面定时更新 · 数据日期 {latestDate || "—"}</span><Link href="/">返回因恒科技主页</Link></footer>
  </main>;
}
