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
  ["buyer", "用户 / 买家", "比价、规格、库存"], ["supplier", "供应商 / 产能方", "价格机会、贸易空间"],
  ["investor", "投资者", "规模、增速、集中度"], ["researcher", "研究者 / 分析师", "来源、口径、缺口"],
] as const;
type Role = typeof roles[number][0];
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
        })).sort((a, b) => Number(a.latest.normalized_usd_per_kg) - Number(b.latest.normalized_usd_per_kg));
        return { speciesId, name: speciesRows[0]?.species_name ?? speciesId, products };
      });
      return { code, name, rows: countryRows, countryMedian, speciesGroups };
    }), [filteredRows, countryFilter]);

  const tradeShares = useMemo(() => {
    const latest = new Map<string, Snapshot<TradeData>>();
    trade.filter(row => row.data.hs && Number.isFinite(Number(row.data.year))).forEach(row => {
      const partner = String(row.data.partner_code ?? "ALL");
      const key = `${row.country}|${row.data.hs}|${row.data.year}|${partner}`;
      const previous = latest.get(key);
      const quality = (item: Snapshot<TradeData>) => item.data.status === "live" ? (item.data.reporting_basis === "importer_official" ? 3 : item.data.reporting_basis === "exporter_mirror" ? 2 : 1) : 0;
      if (!previous || quality(row) > quality(previous) || (quality(row) === quality(previous) && row.capturedAt > previous.capturedAt)) latest.set(key, row);
    });
    const partnerNames: Record<string, string> = { CN: "中国", RU: "俄罗斯", KZ: "哈萨克斯坦", BY: "白俄罗斯", TR: "土耳其" };
    const countryData = countries.map(([code, name]) => {
      const relevant = Array.from(latest.values()).filter(row => row.country === code && row.data.status === "live");
      const years = relevant.filter(row => ["ALL", "0", "ESTIMATE"].includes(String(row.data.partner_code ?? "ALL"))).map(row => Number(row.data.year));
      const year = years.length ? Math.max(...years) : null;
      const yearRows = year == null ? [] : relevant.filter(row => Number(row.data.year) === year);
      const global = yearRows.filter(row => ["ALL", "0"].includes(String(row.data.partner_code ?? "ALL"))).reduce((sum, row) => sum + Number(row.data.value_usd ?? 0), 0);
      const estimates = yearRows.filter(row => String(row.data.partner_code) === "ESTIMATE");
      const estimateLower = estimates.reduce((sum, row) => sum + Number(row.data.estimate_lower_usd ?? 0), 0);
      const estimateUpper = estimates.reduce((sum, row) => sum + Number(row.data.estimate_upper_usd ?? 0), 0);
      const coverage = estimates.length ? estimates.reduce((sum, row) => sum + Number(row.data.coverage_pct ?? 0), 0) / estimates.length : null;
      const confidenceOrder = ["insufficient", "low", "medium", "high"];
      const confidence = estimates.length ? estimates.reduce((lowest, row) => confidenceOrder.indexOf(row.data.confidence ?? "insufficient") < confidenceOrder.indexOf(lowest) ? (row.data.confidence ?? "insufficient") : lowest, "high") : global > 0 ? "official" : "insufficient";
      const partners = Object.keys(partnerNames).map(partner => ({
        code: partner, name: partnerNames[partner], value: yearRows.filter(row => String(row.data.partner_code) === partner).reduce((sum, row) => sum + Number(row.data.value_usd ?? row.data.partner_value_usd ?? 0), 0),
      })).filter(item => item.value > 0).sort((a, b) => b.value - a.value);
      const known = partners.reduce((sum, item) => sum + item.value, 0);
      const marketValue = global > 0 ? global : estimateLower > 0 ? (estimateLower + Math.max(estimateUpper, estimateLower)) / 2 : 0;
      if (marketValue > known) partners.push({ code: "OTHER", name: global > 0 ? "其他来源" : "未覆盖来源", value: marketValue - known });
      const china = partners.find(item => item.code === "CN")?.value ?? 0;
      const basis = global > 0 ? "进口国申报" : estimateLower > 0 ? "伙伴国镜像估算" : "数据不足";
      return { code, name, year, global: marketValue, officialTotal: global, estimateLower, estimateUpper, coverage, confidence, basis, partners, china, share: marketValue > 0 && china > 0 ? china / marketValue * 100 : null };
    });
    const total = countryData.reduce((sum, item) => sum + item.global, 0);
    const china = countryData.reduce((sum, item) => sum + item.china, 0);
    const estimatedCountries = countryData.filter(item => !item.officialTotal && item.estimateLower > 0).length;
    return { countries: countryData, total, china, estimatedCountries, share: total > 0 && china > 0 ? china / total * 100 : null };
  }, [trade]);

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

  return <main className="live-screen">
    <header className="screen-head">
      <div><span>INHEN CENTRAL ASIA INTELLIGENCE</span><h1>中亚菌类市场实时数据中枢</h1></div>
      <div className="screen-status"><i /> 数据链路在线 · POWER BI READY<br/><small>{updated ? `更新于 ${updated.toLocaleTimeString("zh-CN")}` : "正在连接…"}</small></div>
    </header>

    <nav className="screen-roles" aria-label="选择看板角色">
      <div><small>当前视角</small><b>{roleCopy[1]}</b><span>{roleCopy[2]}</span></div>
      {roles.map(([id, name, description]) => <button key={id} className={role === id ? "active" : ""} onClick={() => chooseRole(id)} aria-pressed={role === id}><b>{name}</b><small>{description}</small></button>)}
    </nav>

    <div className="screen-quality">
      <span><i />最新数据日 {latestDate || "—"}</span>
      <b>有效价格 {latestRows.length} 条</b>
      <b>国家覆盖 {stats.countries}/5</b>
      <em>质量等级 {qualitySummary.grade} · 在库率 {qualitySummary.stockRate == null ? "—" : `${qualitySummary.stockRate.toFixed(0)}%`} · 已核验来源 {verifiedTradeSources.length}</em>
      <strong>挂牌价 ≠ 成交价，仅供趋势参考</strong>
    </div>

    <section className="screen-kpis">
      <article><span>有效价格记录</span><b>{rows.length}</b><small>历史有效观察</small></article>
      <article><span>国家覆盖</span><b>{stats.countries}<em>/5</em></b><small>中亚五国</small></article>
      <article><span>菌种覆盖</span><b>{stats.species}</b><small>{speciesOptions.map(([, name]) => name).join("、") || "—"}</small></article>
      <article><span>渠道覆盖</span><b>{stats.platforms}</b><small>公开零售渠道</small></article>
      <article className="range-kpi"><span>{comparableOnly ? "同规格价格范围" : "挂牌价格范围"}</span><b>${priceRange[0].toFixed(2)}—${priceRange[1].toFixed(2)}</b><small>USD/kg · {comparableOnly && dominantQuantity != null ? formatQuantity(dominantQuantity) : "已逐行标注包装规格"}</small></article>
    </section>

    <section className={`role-insights role-${role}`}>
      <header><span>ROLE SIGNALS</span><b>{roleCopy[1]}决策提示</b></header>
      {role === "buyer" && marketSignals.slice(0, 3).map(signal => <article key={signal.speciesId}><small>{signal.name}价格洼地</small><b>{signal.low.country_name ?? signal.low.country} · ${Number(signal.low.normalized_usd_per_kg).toFixed(2)}/kg</b><span>{formatQuantity(signal.low.normalized_quantity_kg)} · 较中位价低 {signal.discount.toFixed(0)}%</span></article>)}
      {role === "supplier" && marketSignals.slice(0, 3).map(signal => <article key={signal.speciesId}><small>{signal.name}高价市场</small><b>{signal.high.country_name ?? signal.high.country} · ${Number(signal.high.normalized_usd_per_kg).toFixed(2)}/kg</b><span>用于发现潜在供给空间，需结合贸易占比核验</span></article>)}
      {role === "investor" && <><article><small>贸易市场规模</small><b>{tradeShares.total ? `$${(tradeShares.total / 1_000_000).toFixed(2)}M` : "—"}</b><span>贸易口径，与零售挂牌价分开</span></article><article><small>中国来源占比</small><b>{tradeShares.share == null ? "—" : `${tradeShares.share.toFixed(1)}%`}</b><span>含镜像估算时以置信标签为准</span></article><article><small>数据质量</small><b>{qualitySummary.grade}</b><span>{verifiedTradeSources.length} 个已核验来源关系</span></article></>}
      {role === "researcher" && <><article><small>价格样本</small><b>{rows.length} 条</b><span>最新批次 {latestDate || "—"}</span></article><article><small>日报汇总</small><b>{daily.length} 组</b><span>质量等级中位数 {qualitySummary.grade}</span></article><article><small>采集运行明细</small><b>暂未返回</b><span>runs/errors 当前为空，不展示虚假成功率</span></article></>}
    </section>

    <nav className="screen-filters" aria-label="数据筛选">
      <div><span>国家</span><button className={countryFilter === "ALL" ? "active" : ""} onClick={() => setCountryFilter("ALL")}>全部</button>{countries.map(([code, name]) => <button className={countryFilter === code ? "active" : ""} onClick={() => setCountryFilter(code)} key={code}>{name}</button>)}</div>
      <div><span>菌种</span><button className={speciesFilter === "ALL" ? "active" : ""} onClick={() => setSpeciesFilter("ALL")}>全部</button>{speciesOptions.map(([id, name]) => <button className={speciesFilter === id ? "active" : ""} onClick={() => setSpeciesFilter(id)} key={id}>{name}</button>)}</div>
      <div><span>规格</span><button className={comparableOnly ? "active" : ""} onClick={() => setComparableOnly(value => !value)} disabled={dominantQuantity == null}>{comparableOnly ? `仅比较 ${formatQuantity(dominantQuantity)}` : "全部规格"}</button><small>同规格模式采用当日样本最多的包装规格，避免跨包装误判。</small></div>
    </nav>

    <section className="screen-grid">
      <article className="screen-map">
        <div className="screen-title price-chart-title"><span>01</span><div><b>中国出口菌类市场占比</b><small>CHINA SHARE OF MUSHROOM IMPORTS</small></div></div>
        <div className="trade-donut-grid">
          <article className="trade-donut-card total">
            <div className={`trade-donut ${tradeShares.share == null ? "empty" : ""}`} style={tradeShares.share == null ? undefined : { background: `conic-gradient(#42e6b0 0 ${tradeShares.share}%, #1b4d68 ${tradeShares.share}% 100%)` }}>
              <div><strong>{tradeShares.share == null ? "—" : `${tradeShares.share.toFixed(1)}%`}</strong><span>中国进口占比</span></div>
            </div>
            <header><b>中亚五国总计</b><small>⚠ 年度数据，非实时</small></header>
            <p>{tradeShares.total > 0 ? `市场规模 $${(tradeShares.total / 1_000_000).toFixed(2)}M${tradeShares.estimatedCountries ? ` · 含 ${tradeShares.estimatedCountries} 国镜像估算` : ""}` : "等待来源国明细"}</p>
          </article>
          {tradeShares.countries.map(country => <article className="trade-donut-card" key={country.code}>
            <div className={`trade-donut small ${country.share == null ? "empty" : ""}`} style={country.share == null ? undefined : { background: `conic-gradient(#42e6b0 0 ${country.share}%, #1b4d68 ${country.share}% 100%)` }}>
              <div><strong>{country.share == null ? "—" : `${country.share.toFixed(1)}%`}</strong><span>中国占比</span></div>
            </div>
            <header><b>{country.name}</b><small>{country.year ?? "—"}</small></header>
            <div className={`trade-confidence confidence-${country.confidence}`}><b>{country.basis}</b><span>{country.confidence === "official" ? "官方" : country.confidence === "high" ? "高置信" : country.confidence === "medium" ? "中置信" : country.confidence === "low" ? "低置信" : "待补充"}{country.coverage != null ? ` · 覆盖 ${country.coverage.toFixed(0)}%` : ""}</span></div>
            {!country.officialTotal && country.estimateLower > 0 && <p className="trade-range">规模区间 ${(country.estimateLower / 1_000_000).toFixed(2)}—${(country.estimateUpper / 1_000_000).toFixed(2)}M USD</p>}
            {country.partners.length ? <div className="trade-legend">{country.partners.slice(0, 5).map(partner => <span key={partner.code} title={`${partner.name} · $${partner.value.toLocaleString("en-US")}`}><i className={`partner-${partner.code.toLowerCase()}`} />{partner.name} {country.global > 0 ? `${(partner.value / country.global * 100).toFixed(1)}%` : "—"}</span>)}</div> : <p>等待来源国明细</p>}
          </article>)}
        </div>
        {(role === "supplier" || role === "investor") && tradeTrend.length > 1 && <div className="trade-history">
          <header><b>食用菌进口年度序列</b><small>贸易口径 · USD</small></header>
          <div>{tradeTrend.map(point => { const max = Math.max(...tradeTrend.map(item => item.value), 1); return <span key={point.year}><i style={{height: `${Math.max(8, point.value / max * 100)}%`}} /><b>{point.year}</b><small>${(point.value / 1_000_000).toFixed(1)}M</small></span>; })}</div>
        </div>}
        <p className="trade-method">口径：中亚五国食用菌（HS 070951 / 070959 / 200310）进口贸易，单位 USD。优先采用进口国申报；缺失时采用中国及主要伙伴国出口镜像，并显示覆盖率、规模区间与置信等级。已核验来源 {verifiedTradeSources.length} 个：UN Comtrade、中国海关统计、塔吉克斯坦国家统计局、土库曼斯坦国家统计委员会及海关；年度数据。</p>
      </article>

      <article className="screen-feed">
        <div className="screen-title"><span>02</span><div><b>国家与菌种价格观察</b><small>COUNTRY → SPECIES → SKU</small></div></div>
        {error && <p className="screen-error">数据连接异常：{error}</p>}
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
            </article>)}</div> : <p className="country-collecting">当前筛选下暂无有效价格</p>}
          </section>)}
          {!rows.length && !error && <p className="screen-empty">等待五国自动化采集写入数据…</p>}
        </div>
      </article>
    </section>

    <footer className="screen-footer"><span>数据源：Cloudflare D1 · 每 60 秒自动刷新 · 数据版本 {latestDate || "—"}</span><Link href="/">返回因恒科技主页</Link><a href={API} target="_blank" rel="noreferrer">Power BI 数据接口 →</a></footer>
  </main>;
}
