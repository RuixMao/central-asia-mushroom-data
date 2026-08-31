"use client";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { mirrorRecords } from "../../data";
import {
  countryNames,
  latestByCountry,
  loadLivePrices,
  rowPrice,
  speciesLabel,
  type LivePriceRow,
} from "../../market-display";
export default function MarketDetail({ code }: { code: string }) {
  const [rows, setRows] = useState<LivePriceRow[]>([]);
  const [ready, setReady] = useState(false);
  useEffect(() => {
    loadLivePrices()
      .then(setRows)
      .finally(() => setReady(true));
  }, []);
  const country = Boolean(countryNames[code]);
  const scope = country ? code : code.toLowerCase();
  const prices = useMemo(
    () => latestByCountry(rows).filter((row) => country ? row.country === code : row.species_id === scope),
    [rows, code, country, scope],
  );
  const trade = country ? mirrorRecords.filter((row) => row.countryCode === code) : [];
  const channels = Array.from(new Set(prices.map((row) => row.platform_name)));
  const latest = prices.reduce(
    (date, row) => (row.observation_date > date ? row.observation_date : date),
    "",
  );
  const verified = prices.filter(
    (row) => row.validation_status === "valid",
  ).length;
  return (
    <main className="saas-main market-detail-page">
      <section className="saas-hero compact">
        <span>{country ? `${code} · 国家市场` : "菌种市场"}</span>
        <h1>{country ? countryNames[code] : speciesLabel(scope)}</h1>
        <p>价格、贸易与渠道信息在同一页面展开显示，可通过页面目录直达。</p>
        <nav className="market-anchor-nav">
          <a href="#prices">价格</a>
          {country && <a href="#trade">贸易</a>}
          <a href="#channels">渠道</a>
          {code === "LA" && <a href="#laos-depth">老挝市场参考</a>}
        </nav>
      </section>
      <section id="prices" className="market-data-section">
        <header>
          <div>
            <span>当地价格</span>
            <h2>公开挂牌价格</h2>
          </div>
          <small>更新于 {latest || "—"}</small>
        </header>
        {!ready ? (
          <div className="price-skeleton">
            <i />
            <i />
            <i />
          </div>
        ) : prices.length ? (
          <div className="market-price-list">
            {prices.map((row, index) => (
              <article key={`${row.species_id}-${row.platform_name}-${index}`}>
                <div>
                  <b>{speciesLabel(row.species_id)}</b>
                  <span>{row.city || countryNames[code]}</span>
                </div>
                <strong>{rowPrice(row)}</strong>
                <small>{row.platform_name}</small>
                <em>
                  {row.validation_status === "valid" ? "已核验" : "市场观察"}
                </em>
              </article>
            ))}
          </div>
        ) : (
          <div className="market-neutral-state">
            <b>该市场已有贸易与渠道信息</b>
            <span>具体零售价格将在取得数字报价后直接展示。</span>
          </div>
        )}
        <p className="market-status-line">
          共 {prices.length} 条价格观察，其中 {verified} 条已核验。
        </p>
      </section>
      <section id="trade" className="market-data-section">
        <header>
          <div>
            <span>贸易规模</span>
            <h2>进口与品类结构</h2>
          </div>
          <small>更新于 2024</small>
        </header>
        {trade.length ? (
          <div className="market-trade-list">
            {trade.map((row) => (
              <article key={row.hs}>
                <span>HS {row.hs}</span>
                <b>{row.product}</b>
                <strong>
                  $
                  {Number(
                    row.importerCifUsd ?? row.confirmedTradeUsd ?? 0,
                  ).toLocaleString("en-US")}
                </strong>
                <em>数据等级 {row.confidence}</em>
              </article>
            ))}
          </div>
        ) : (
          <div className="market-neutral-state">
            <b>贸易金额暂未形成同口径记录</b>
            <span>可先使用本页价格与渠道信息判断零售端价格空间。</span>
          </div>
        )}
      </section>
      <section id="channels" className="market-data-section">
        <header>
          <div>
            <span>销售渠道</span>
            <h2>已出现价格的渠道</h2>
          </div>
          <small>更新于 {latest || "—"}</small>
        </header>
        {channels.length ? (
          <div className="market-channel-list">
            {channels.map((channel) => (
              <span key={channel}>{channel}</span>
            ))}
          </div>
        ) : (
          <div className="market-neutral-state">
            <b>暂无公开数字报价渠道</b>
            <span>可通过市场验证服务核对当地渠道。</span>
          </div>
        )}
      </section>
      {code === "LA" && (
        <section id="laos-depth" className="market-data-section laos-depth">
          <header>
            <div>
              <span>老挝市场参考</span>
              <h2>历史基准、邻国价格与渠道</h2>
            </div>
            <small>更新于 {latest || "—"}</small>
          </header>
          <div className="laos-reference-grid">
            <article>
              <b>历史基准</b>
              <p>
                平菇、香菇、木耳历史价格与现有数字报价分开呈现，用于观察价格结构。
              </p>
            </article>
            <article>
              <b>泰国价格参考</b>
              <p>泰国同品种零售价格用于比较区域供给，不替代老挝当地成交价。</p>
            </article>
            <article>
              <b>渠道清单</b>
              <p>
                {channels.length
                  ? channels.join("、")
                  : "万象商超、电商与菜市场渠道"}
              </p>
            </article>
          </div>
        </section>
      )}
      <section className="market-detail-action">
        <Link href="/market">比较全部价格</Link>
        <Link href="/expand/contact">咨询市场进入条件</Link>
      </section>
    </main>
  );
}
