"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "./native-link";
import { mirrorRecords, opportunities } from "./data";
import {
  loadLivePrices,
  marketCodesFromRows,
  marketName,
  rowPrice,
  speciesLabel,
  speciesPriority,
} from "./market-display";
import { southeastAsiaCodes, targetMarketCodes, targetMarketNames } from "./market-scope";

type PriceRow = {
  observation_date: string;
  country: string;
  country_name?: string;
  species_id: string;
  species_name?: string;
  platform_name: string;
  original_title: string;
  normalized_usd_per_kg: number | null;
  current_price: number | null;
  currency: string;
  package_value: number | null;
  package_unit: string | null;
  raw_price_text?: string;
  price_usd_per_package?: number | null;
  usd_rate_local_per_usd?: number | null;
  fx_source?: string | null;
  fx_timestamp?: string | null;
  is_current?: boolean;
};
type Report = {
  slug?: string;
  title: string;
  summary?: string;
  type: string;
  date?: string;
  publishedAt?: string | number | Date;
};
const countryNames = targetMarketNames;
const countryCodes = [...targetMarketCodes];
const speciesName = (row: PriceRow) => speciesLabel(row.species_id);
const money = (value: number) =>
  value
    ? value >= 1_000_000
      ? `$${(value / 1_000_000).toFixed(2)}M`
      : `$${Math.round(value / 1000).toLocaleString("zh-CN")}K`
    : "—";
const range = (values: number[]) =>
  values.length
    ? `$${Math.min(...values).toFixed(2)}–$${Math.max(...values).toFixed(2)}/kg`
    : "—";
const balancedRows = (rows: PriceRow[], limit = 20) => {
  const sorted = [...rows].sort(
    (a, b) =>
      speciesPriority(a.species_id) - speciesPriority(b.species_id) ||
      Number(b.normalized_usd_per_kg ?? 0) -
        Number(a.normalized_usd_per_kg ?? 0),
  );
  const kept = sorted.filter(
    (row, index, all) =>
      all
        .slice(0, index)
        .filter(
          (item) =>
            item.country === row.country && item.species_id === row.species_id,
        ).length < 2,
  );
  const buckets = marketCodesFromRows(kept).map((code) =>
    kept.filter((row) => row.country === code),
  );
  const result: PriceRow[] = [];
  for (
    let index = 0;
    result.length < limit && buckets.some((bucket) => index < bucket.length);
    index++
  )
    for (const bucket of buckets)
      if (bucket[index] && result.length < limit) result.push(bucket[index]);
  return result;
};

function usePrices() {
  const [rows, setRows] = useState<PriceRow[]>([]);
  const [ready, setReady] = useState(false);
  useEffect(() => {
    loadLivePrices()
      .then((records) => setRows(records as PriceRow[]))
      .catch(() => setRows([]))
      .finally(() => setReady(true));
  }, []);
  const latest = useMemo(
    () =>
      rows.reduce(
        (d, r) => (r.observation_date > d ? r.observation_date : d),
        "",
      ),
    [rows],
  );
  const today = useMemo(() => {
    const latestByCountry = new Map<string, string>();
    for (const row of rows)
      if (row.observation_date > (latestByCountry.get(row.country) ?? ""))
        latestByCountry.set(row.country, row.observation_date);
    return rows.filter(
      (row) => row.observation_date === latestByCountry.get(row.country),
    );
  }, [rows]);
  return { rows, today, latest, ready };
}

export function MarketLivePreview() {
  const { today, latest, ready } = usePrices();
  const species = useMemo(
    () =>
      Array.from(
        new Map(today.map((r) => [r.species_id, speciesName(r)])).entries(),
      ).map(([id, name]) => ({
        id,
        name,
        count: today.filter((r) => r.species_id === id).length,
      })),
    [today],
  );
  const comparable = useMemo(() => today.filter((row) => row.normalized_usd_per_kg != null), [today]);
  const displayable = today.filter((row) => row.is_current !== false);
  const visible = useMemo(() => balancedRows(displayable, 12), [displayable]);
  const summary = useMemo(() => {
    const countries = new Set(displayable.map((row) => row.country)).size;
    const channels = new Set(
      displayable.map((row) => `${row.country}-${row.platform_name}`),
    ).size;
    const speciesCount = new Set(displayable.map((row) => row.species_id)).size;
    const widest = countryCodes
      .map((code) => {
        const values = comparable
          .filter((row) => row.country === code)
          .map((row) => Number(row.normalized_usd_per_kg));
        return {
          code,
          spread: values.length ? Math.max(...values) - Math.min(...values) : 0,
        };
      })
      .sort((a, b) => b.spread - a.spread)[0];
    return { countries, channels, speciesCount, widest };
  }, [comparable,displayable]);
  return (
    <>
    <section className="market-summary-strip" aria-label="价格行情摘要">
      <article><span>覆盖市场</span><strong>{ready ? summary.countries : "—"} 个国家</strong><small>包含原币挂牌价及可换算价格</small></article>
      <article><span>渠道与品种</span><strong>{ready ? summary.channels : "—"} 个渠道</strong><small>{ready ? `${summary.speciesCount} 个规范品种` : "正在读取"}</small></article>
      <article><span>优先观察</span><strong>{ready && summary.widest?.spread ? countryNames[summary.widest.code] : "—"}</strong><small>当前公开价格跨度较大，需结合规格与渠道解释</small></article>
    </section>
    <section className="theme-data-grid market-price-overview">
      <article className="theme-data-card wide">
        <header>
          <div>
            <span>可比价格</span>
            <h2>各市场近期公开挂牌价</h2>
          </div>
          <small>更新至 {latest || "—"}</small>
        </header>
        <div className="theme-table">
          <div className="theme-row head">
            <span>国家</span>
            <span>品类</span>
            <span>价格</span>
            <span>平台</span>
          </div>
          {visible.map((r, i) => (
            <div
              className="theme-row"
              key={`${r.country}-${r.platform_name}-${i}`}
            >
              <span>{marketName(r)}</span>
              <span>{speciesName(r)}</span>
              <strong>{rowPrice(r)}</strong>
              <span>{r.platform_name}</span>
            </div>
          ))}
          {ready && !displayable.length && (
            <p className="theme-empty">— 暂无公开价格</p>
          )}
        </div>
        <small className="theme-source">括号内美元价按各条记录采集日汇率折算。</small>
        <a href="/market/prices">筛选完整价格 →</a>
      </article>
      <article className="theme-data-card">
        <header>
          <div>
            <span>品类覆盖</span>
            <h2>当前覆盖品种</h2>
          </div>
        </header>
        {species.length ? (
          <div className="theme-chip-list">
            {species.map((s) => (
              <div key={s.id}>
                <b>{s.name}</b>
                <span>{s.count} 条市场报价</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="theme-empty">— 暂无公开报价</p>
        )}
        <a href="/market/prices">按品种筛选价格 →</a>
      </article>
    </section>
    </>
  );
}

export function InsightsLivePreview() {
  const { today, latest } = usePrices();
  const hs = useMemo(
    () =>
      ["070951", "070959", "200310"].map((code) => ({
        code,
        total: mirrorRecords
          .filter((r) => r.hs === code)
          .reduce(
            (s, r) => s + Number(r.importerCifUsd ?? r.confirmedTradeUsd ?? 0),
            0,
          ),
      })),
    [],
  );
  return (
    <section className="theme-data-grid three">
      <article className="theme-data-card">
        <header>
          <div>
              <span>国别需求</span>
            <h2>国别需求画像</h2>
          </div>
          <small>价格截至 {latest || "—"}</small>
        </header>
        <div className="theme-country-list">
          {countryCodes.map((code) => {
            const trade = mirrorRecords.filter((r) => r.countryCode === code);
            const total = trade.reduce(
              (s, r) =>
                s + Number(r.importerCifUsd ?? r.confirmedTradeUsd ?? 0),
              0,
            );
            const china = trade.reduce(
              (s, r) => s + Number(r.chinaFobUsd ?? 0),
              0,
            );
            const prices = today
              .filter((r) => r.country === code)
              .map((r) => Number(r.normalized_usd_per_kg))
              .filter(Number.isFinite);
            return (
              <div key={code}>
                <b>{countryNames[code]}</b>
                <span>进口 {money(total)}</span>
                <span>
                  中国占比{" "}
                  {total && trade.some((r) => r.chinaFobUsd != null)
                    ? `${((china / total) * 100).toFixed(1)}%`
                    : "—"}
                </span>
                <span>零售价 {range(prices)}</span>
              </div>
            );
          })}
        </div>
      </article>
      <article className="theme-data-card">
        <header>
          <div>
              <span>贸易结构</span>
            <h2>规模与品类结构</h2>
          </div>
        </header>
        <div className="theme-metric-list">
          {hs.map((item) => (
            <div key={item.code}>
              <span>HS {item.code}</span>
              <strong>{money(item.total)}</strong>
            </div>
          ))}
        </div>
        <small className="theme-source">
          来源：UN Comtrade 2024 进口申报及伙伴国贸易记录。
        </small>
      </article>
      <article className="theme-data-card">
        <header>
          <div>
              <span>渠道覆盖</span>
            <h2>平台与覆盖品类</h2>
          </div>
        </header>
        <div className="theme-country-list">
          {countryCodes.map((code) => {
            const rows = today.filter((r) => r.country === code);
            return (
              <div key={code}>
                <b>{countryNames[code]}</b>
                <span>
                  {new Set(rows.map((r) => r.platform_name)).size || "—"} 个渠道
                </span>
                <span>
                  {new Set(rows.map((r) => r.species_id)).size || "—"} 个菌种
                </span>
                <span>{rows.length ? "已有报价" : "欢迎咨询"}</span>
              </div>
            );
          })}
        </div>
      </article>
    </section>
  );
}

export function ExpandLivePreview() {
  const [report, setReport] = useState<Report | null>(null);
  useEffect(() => {
    fetch("/api/ingest/report", { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((p) => setReport(p.records?.[0] ?? null))
      .catch(() => {});
  }, []);
  return (
    <>
      <section className="theme-data-grid expand-intelligence-grid">
        <article className="theme-data-card">
          <span>案例图谱</span>
          <h2>企业拓展路径</h2>
          <p className="theme-empty">案例收集中</p>
          <small>仅收录具备公开来源、可回溯核验的企业案例。</small>
          <Link href="/expand/cases">查看案例库 →</Link>
        </article>
        <article className="theme-data-card daily-intelligence-card">
          <header>
            <div>
              <span>每日菌情</span>
              <h2>{report?.title ?? "最新报告暂未发布"}</h2>
            </div>
            <small>
              {report
                ? (report.date ??
                  (report.publishedAt
                    ? new Date(report.publishedAt).toLocaleDateString("zh-CN")
                    : "—"))
                : "—"}
            </small>
          </header>
          <p>
            {report?.summary ?? "当日价格、渠道与政策证据尚未形成可发布结论。"}
          </p>
          <div className="daily-intelligence-actions">
            <a
              className="theme-primary-link"
              href={
                report?.slug
                  ? `/reports/${encodeURIComponent(report.slug)}`
                  : "/reports"
              }
            >
              阅读今日菌情 →
            </a>
            <a href="/expand/daily">查看历史日报</a>
          </div>
        </article>
        <article className="theme-data-card">
          <span>合作对接</span>
          <h2>提交出海需求</h2>
          <p>面向产能方、渠道商、技术与服务机构。</p>
          <a className="theme-primary-link" href="/expand/contact">
            发起合作对接 →
          </a>
        </article>
      </section>
      <OpportunityRadar compact />
    </>
  );
}

export function OpportunityRadar({ compact = false }: { compact?: boolean }) {
  const [region, setRegion] = useState<"ALL" | "SEA" | "CA">("ALL");
  const seaCodes = [...southeastAsiaCodes];
  const orderedCodes = [...targetMarketCodes];
  const regionOpportunities = opportunities.filter((item) =>
    region === "ALL"
      ? true
      : region === "SEA"
        ? seaCodes.includes(item.countryCode)
        : !seaCodes.includes(item.countryCode),
  );
  const visible = compact
    ? opportunities.filter((item) => ["LA", "VN", "KZ"].includes(item.countryCode)).slice(0, 3)
    : regionOpportunities;
  const countryGroups = orderedCodes
    .map((code) => ({ code, items: visible.filter((item) => item.countryCode === code) }))
    .filter((group) => group.items.length);
  const stages = ["发现信号", "补充证据", "成本测算", "渠道验证", "报价/打样"];
  return (
    <section
      className={`opportunity-radar ${compact ? "compact" : "full"}`}
      aria-label="商机雷达"
    >
      <header className="opportunity-radar-head">
        <div>
          <span>OPPORTUNITY RADAR</span>
          <h2>按国家查看市场机会</h2>
          <p>
            东南亚以价格与渠道验证为主，中亚同时结合贸易规模与变化。先看国家，再决定需要补充哪些落地条件。
          </p>
        </div>
        {compact && <a href="/opportunities">查看全部市场机会 →</a>}
      </header>
      {!compact && <nav className="opportunity-region-tabs" aria-label="选择商机区域">
        {[["ALL", "全部市场"], ["SEA", "东南亚"], ["CA", "中亚"]].map(([value, label]) => <button type="button" key={value} className={region === value ? "active" : ""} aria-pressed={region === value} onClick={() => setRegion(value as "ALL" | "SEA" | "CA")}>{label}</button>)}
      </nav>}
      <div className="opportunity-country-groups">
        {countryGroups.map((group) => <section className="opportunity-country-group" key={group.code} aria-labelledby={`opportunity-${group.code}`}>
          <header><div><span>{seaCodes.includes(group.code) ? "东南亚市场" : "中亚市场"}</span><h3 id={`opportunity-${group.code}`}>{countryNames[group.code]}</h3></div><a href={`/markets/${group.code}`}>查看国家工作台 →</a></header>
          <div className="opportunity-radar-grid">{group.items.map((item, index) => (
          <article key={item.id}>
            <div className="radar-rank">
              <span>
                {String(index + 1).padStart(2, "0")} · {item.product}
              </span>
            </div>
            <div className="radar-tags">
              <b>{item.status}</b>
              <span>{seaCodes.includes(item.countryCode) ? "价格与渠道验证" : "贸易与市场验证"}</span>
            </div>
            <h4>{item.signal}</h4>
            <div className="radar-progress" aria-label="验证进度">
              {stages.map((stage, stageIndex) => (
                <span
                  className={
                    stageIndex === 0
                      ? "done"
                      : stageIndex === 1 && item.status !== "暂缓"
                        ? "active"
                        : ""
                  }
                  key={stage}
                >
                  {stage}
                </span>
              ))}
            </div>
            <div className="radar-next">
              <span>决策关注点</span>
              <b>{item.nextAction}</b>
            </div>
            <footer>
              <span>{item.hs.startsWith("0") || item.hs.startsWith("2") ? `HS ${item.hs}` : item.hs}</span>
              {item.marketUsd > 0 && <span>市场规模 {money(item.marketUsd)}</span>}
              {item.change !== 0 && <span>
                {item.change > 0 ? "+" : ""}
                {item.change}%
              </span>}
            </footer>
            {!compact && (
              <div className="radar-actions">
                <a href={`/markets/${item.countryCode}`}>
                  查看市场证据
                </a>
                <button type="button" onClick={() => window.print()}>
                  打印机会卡
                </button>
                <a href="/expand/contact">申请进一步验证</a>
              </div>
            )}
          </article>
          ))}</div>
        </section>)}
      </div>
      {!compact && (
        <div className="radar-method">
          <b>信号说明</b>
          <span>优先验证：证据较强且值得立即核验</span>
          <span>值得跟进：具备一定市场基础</span>
          <span>信息有限：公开价格、渠道或贸易信息仍有限</span>
          <span>暂缓：当前风险或口径问题高于机会信号</span>
        </div>
      )}
    </section>
  );
}
