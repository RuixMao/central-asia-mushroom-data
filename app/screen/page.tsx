"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

type PriceRow = {
  observation_date: string;
  country: string;
  country_name?: string;
  city: string;
  species_id: string;
  species_name?: string;
  product_form: string;
  platform_name: string;
  original_title: string;
  currency: string;
  current_price: number;
  normalized_usd_per_kg: number | null;
  in_stock: number;
};

const API = "https://api.yinheng.site/api/powerbi?table=prices";
const countries = [
  ["KZ", "哈萨克斯坦", "阿拉木图"], ["UZ", "乌兹别克斯坦", "塔什干"],
  ["KG", "吉尔吉斯斯坦", "比什凯克"], ["TJ", "塔吉克斯坦", "杜尚别"],
  ["TM", "土库曼斯坦", "阿什哈巴德"],
];

export default function ScreenPage() {
  const [rows, setRows] = useState<PriceRow[]>([]);
  const [updated, setUpdated] = useState<Date | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const response = await fetch(API, { cache: "no-store" });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const payload = await response.json();
        if (active) { setRows(payload.records ?? []); setUpdated(new Date()); setError(""); }
      } catch (reason) {
        if (active) setError(reason instanceof Error ? reason.message : "数据连接失败");
      }
    };
    load();
    const timer = window.setInterval(load, 60_000);
    return () => { active = false; window.clearInterval(timer); };
  }, []);

  const stats = useMemo(() => {
    const valid = rows.filter(row => Number.isFinite(row.normalized_usd_per_kg));
    const average = valid.length ? valid.reduce((sum, row) => sum + Number(row.normalized_usd_per_kg), 0) / valid.length : 0;
    return { countries: new Set(rows.map(row => row.country)).size, species: new Set(rows.map(row => row.species_id)).size, platforms: new Set(rows.map(row => row.platform_name)).size, average };
  }, [rows]);

  return <main className="live-screen">
    <header className="screen-head">
      <div><span>INHEN CENTRAL ASIA INTELLIGENCE</span><h1>中亚菌类市场实时数据中枢</h1></div>
      <div className="screen-status"><i /> 数据链路在线<br/><small>{updated ? `更新于 ${updated.toLocaleTimeString("zh-CN")}` : "正在连接…"}</small></div>
    </header>

    <section className="screen-kpis">
      <article><span>有效价格记录</span><b>{rows.length}</b><small>POWER BI READY</small></article>
      <article><span>国家覆盖</span><b>{stats.countries}<em>/5</em></b><small>CENTRAL ASIA</small></article>
      <article><span>菌种覆盖</span><b>{stats.species}</b><small>SPECIES</small></article>
      <article><span>渠道覆盖</span><b>{stats.platforms}</b><small>PLATFORMS</small></article>
      <article><span>均价</span><b>${stats.average.toFixed(2)}</b><small>USD / KG</small></article>
    </section>

    <section className="screen-grid">
      <article className="screen-map">
        <div className="screen-title"><span>01</span><div><b>五国数据覆盖</b><small>COUNTRY COVERAGE</small></div></div>
        <div className="country-network">
          <strong className="network-core">因恒<br/><small>喀什中枢</small></strong>
          {countries.map(([code, name, city], index) => {
            const count = rows.filter(row => row.country === code).length;
            return <div className={`country-node node-${index}`} key={code}><i className={count ? "on" : ""}/><b>{name}</b><span>{city}</span><em>{count ? `${count} RECORDS` : "COLLECTING"}</em></div>;
          })}
        </div>
      </article>

      <article className="screen-feed">
        <div className="screen-title"><span>02</span><div><b>实时价格观察</b><small>LIVE PRICE FEED</small></div></div>
        {error && <p className="screen-error">数据连接异常：{error}</p>}
        <div className="price-feed">
          {rows.slice(0, 10).map((row, index) => <div className="feed-row" key={`${row.original_title}-${index}`}>
            <span>{row.observation_date}<small>{row.country_name ?? row.country} · {row.city}</small></span>
            <b>{row.species_name ?? row.species_id}<small>{row.platform_name}</small></b>
            <em>${row.normalized_usd_per_kg?.toFixed(2) ?? "—"}<small>USD / 公斤</small></em>
          </div>)}
          {!rows.length && !error && <p className="screen-empty">等待五国自动化采集写入数据…</p>}
        </div>
      </article>
    </section>

    <footer className="screen-footer"><span>数据源：独立 Cloudflare D1 · 每 60 秒自动刷新</span><Link href="/">返回因恒科技主页</Link><a href={API} target="_blank" rel="noreferrer">Power BI 数据接口 ↗</a></footer>
  </main>;
}
