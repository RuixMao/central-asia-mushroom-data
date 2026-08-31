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
type TradeSnapshot = { country:string; source:string; data:{ hs?:string; year?:number; partner_code?:string; value_usd?:number|null; estimate_lower_usd?:number|null; estimate_upper_usd?:number|null; status?:string } };
const tradeProductNames:Record<string,string>={"070951":"鲜或冷藏双孢蘑菇","070959":"其他鲜或冷藏蘑菇","200310":"加工保藏蘑菇"};
export default function MarketDetail({ code }: { code: string }) {
  const [rows, setRows] = useState<LivePriceRow[]>([]);
  const [tradeSnapshots,setTradeSnapshots]=useState<TradeSnapshot[]>([]);
  const [ready, setReady] = useState(false);
  useEffect(() => {
    loadLivePrices()
      .then(setRows)
      .finally(() => setReady(true));
  }, []);
  const country = Boolean(countryNames[code]);
  useEffect(()=>{if(!country)return;fetch(`/api/ingest/snapshot?metric=trade&country=${code}&limit=10000`,{cache:"no-store"}).then(async response=>response.ok?response.json():{records:[]}).then((payload:{records?:TradeSnapshot[]})=>setTradeSnapshots(payload.records??[])).catch(()=>setTradeSnapshots([]))},[code,country]);
  const scope = country ? code : code.toLowerCase();
  const prices = useMemo(
    () => latestByCountry(rows).filter((row) => country ? row.country === code : row.species_id === scope),
    [rows, code, country, scope],
  );
  const legacyTrade = country ? mirrorRecords.filter((row) => row.countryCode === code) : [];
  const tradeYears=tradeSnapshots.filter(row=>row.data.status==="live"&&(row.data.value_usd!=null||row.data.estimate_lower_usd!=null)).map(row=>Number(row.data.year??0));
  const tradeYear=tradeYears.length?Math.max(...tradeYears):legacyTrade.length?2024:0;
  const currentTrade=tradeSnapshots.filter(row=>row.data.status==="live"&&row.data.year===tradeYear&&(row.data.value_usd!=null||row.data.estimate_lower_usd!=null));
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
          <small>更新于 {tradeYear || "—"}</small>
        </header>
        {currentTrade.length ? (
          <div className="market-trade-list">
            {currentTrade.map((row,index) => {
              const marketSize=row.data.partner_code==="MARKET_SIZE";
              const value=Number(row.data.value_usd??row.data.estimate_lower_usd??0);
              return <article key={`${row.data.hs??"market"}-${row.source}-${index}`}>
                <span>{marketSize?"市场规模":`HS ${row.data.hs}`}</span>
                <b>{marketSize?"食用菌进口市场规模":tradeProductNames[row.data.hs??""]??"食用菌产品"}</b>
                <strong>${value.toLocaleString("en-US",{maximumFractionDigits:0})}</strong>
                <em>{row.source}</em>
              </article>
            })}
          </div>
        ) : legacyTrade.length ? (
          <div className="market-trade-list">
            {legacyTrade.map((row) => (
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
            <b>暂无可展示的食用菌贸易金额</b>
            <span>可先查看本页价格与渠道信息。</span>
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
