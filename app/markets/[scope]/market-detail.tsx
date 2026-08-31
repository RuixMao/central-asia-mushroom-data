"use client";
import Link from "../../native-link";
import { useEffect, useMemo, useState } from "react";
import { mirrorRecords } from "../../data";
import {
  countryNames,
  loadLivePrices,
  marketName,
  rowPrice,
  speciesLabel,
  type LivePriceRow,
} from "../../market-display";
import {marketReadiness} from "../../market-readiness";
import {targetMarkets} from "../../market-scope";
type TradeSnapshot = { country:string; source:string; data:{ hs?:string; year?:number; partner_code?:string; value_usd?:number|null; estimate_lower_usd?:number|null; estimate_upper_usd?:number|null; status?:string } };
const tradeProductNames:Record<string,string>={"070951":"鲜或冷藏双孢蘑菇","070959":"其他鲜或冷藏蘑菇","200310":"加工保藏蘑菇"};
export default function MarketDetail({ code }: { code: string }) {
  const [rows, setRows] = useState<LivePriceRow[]>([]);
  const [tradeSnapshots,setTradeSnapshots]=useState<TradeSnapshot[]>([]);
  const [ready, setReady] = useState(false);
  useEffect(() => {
    loadLivePrices()
      .then(setRows)
      .catch(() => setRows([]))
      .finally(() => setReady(true));
  }, []);
  const country = /^[A-Z]{2}$/.test(code);
  useEffect(()=>{if(!country)return;fetch(`/api/ingest/snapshot?metric=trade&country=${code}&limit=10000`,{cache:"no-store"}).then(async response=>response.ok?response.json():{records:[]}).then((payload:{records?:TradeSnapshot[]})=>setTradeSnapshots(payload.records??[])).catch(()=>setTradeSnapshots([]))},[code,country]);
  const scope = country ? code : code.toLowerCase();
  const prices = useMemo(
    () => rows.filter((row) => country ? row.country === code : row.species_id === scope),
    [rows, code, country, scope],
  );
  const pageRows=prices;
  const directRows=pageRows.filter(row=>["A","B","C","D"].includes(row.grade??""));
  const historyRows=pageRows.filter(row=>row.grade==="D");
  const neighborRows=pageRows.filter(row=>row.grade==="E");
  const readiness=marketReadiness(pageRows);
  const displayCountryName=pageRows[0]?marketName(pageRows[0]):countryNames[code]??code;
  const legacyTradeAll = country ? mirrorRecords.filter((row) => row.countryCode === code) : [];
  const legacyYear = legacyTradeAll.length ? Math.max(...legacyTradeAll.map(row => row.year ?? 2024)) : 0;
  const legacyTrade = legacyTradeAll.filter(row => (row.year ?? 2024) === legacyYear);
  const tradeYears=tradeSnapshots.filter(row=>row.data.status==="live"&&(row.data.value_usd!=null||row.data.estimate_lower_usd!=null)).map(row=>Number(row.data.year??0));
  const tradeYear=tradeYears.length?Math.max(...tradeYears):legacyYear;
  const currentTrade=tradeSnapshots.filter(row=>row.data.status==="live"&&row.data.year===tradeYear&&(row.data.value_usd!=null||row.data.estimate_lower_usd!=null));
  const channels = Array.from(new Set(pageRows.map((row) => row.platform_name).filter(Boolean)));
  const liveLatest = pageRows.reduce(
    (date, row) => (row.observation_date > date ? row.observation_date : date),
    "",
  );
  const latest = liveLatest;
  const configuredChannels=targetMarkets.find(market=>market.code===code)?.channels.map(channel=>{try{return new URL(channel.url).hostname.replace(/^www\./,"")}catch{return channel.id}})??[];
  return (
    <main className="saas-main market-detail-page">
      <section className="saas-hero compact">
        <span>{country ? `${code} · 国家市场` : "菌种市场"}</span>
        <h1>{country ? displayCountryName : speciesLabel(scope)}</h1>
        <p>公开价格、海关贸易与销售渠道。</p>
        <nav className="market-anchor-nav">
          <a href="#prices">价格</a>
          {country && <a href="#trade">贸易</a>}
          <a href="#channels">渠道</a>
          {country && <a href="#market-reference">市场参考</a>}
        </nav>
      </section>
      <section id="prices" className="market-data-section">
        <header>
          <div>
            <span>当地价格</span>
            <h2>公开挂牌价格</h2>
          </div>
          <small>{latest?`更新于 ${latest}`:"数据采集中"}</small>
        </header>
        {readiness.level==="L1"&&<p className="market-state-note">该国直接报价数据采集中，以下为已有记录与参考数据</p>}
        {!ready && !country ? (
          <div className="price-skeleton">
            <i />
            <i />
            <i />
          </div>
        ) : directRows.length ? (
          <div className="market-price-list">
            {directRows.map((row, index) => (
              <article key={`${row.species_id}-${row.platform_name}-${index}`}>
                <div>
                  <b>{row.original_title||speciesLabel(row.species_id)}</b>
                  <span>{row.city || displayCountryName}</span>
                </div>
                <strong>{rowPrice(row)}</strong>
                <small>{row.platform_name} · {row.source_type||"公开来源"}</small>
                <em>{row.grade?`${row.grade} 级`:"等级待补"}</em>
                {row.source_url?<a href={row.source_url} target="_blank" rel="noreferrer">查看来源</a>:<span>来源链接待补</span>}
              </article>
            ))}
          </div>
        ) : (
          <div className="market-neutral-state">
            <b>该国公开报价采集中</b>
            <span>预计覆盖品种：平菇、香菇、木耳</span>
          </div>
        )}
        <p className="market-status-line">
          {readiness.level==="L0"?`更新于 ${latest} · ${readiness.N} 条公开报价`:readiness.level==="L1"?`已收录 ${readiness.N} 条公开报价 · ${latest} 更新`:`公开报价持续更新`}
        </p>
        {directRows.length>0&&<p className="theme-source">括号内美元价按各条记录采集日汇率折算。</p>}
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
                <em>UN Comtrade · {row.year ?? 2024}</em>
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
            <h2>渠道清单</h2>
          </div>
          <small>{latest?`更新于 ${latest}`:"数据采集中"}</small>
        </header>
        {channels.length||configuredChannels.length ? (
          <div className="market-channel-list">
            {(channels.length?channels:configuredChannels).map((channel) => (
              <span key={channel}>{channel}</span>
            ))}
          </div>
        ) : (
          <div className="market-neutral-state">
            <b>渠道清单采集中</b>
            <span>计划覆盖当地主要商超、电商平台与农贸市场。</span>
          </div>
        )}
      </section>
      {country && (
        <section id="market-reference" className="market-data-section laos-depth">
          <header>
            <div>
              <span>市场参考</span>
              <h2>历史基准、邻国价格与渠道</h2>
            </div>
            <small>{latest?`更新于 ${latest}`:"数据采集中"}</small>
          </header>
          <div className="laos-reference-grid">
            <article>
              <b>历史基准</b>
              <p>{historyRows.length?historyRows.map(row=>`${speciesLabel(row.species_id)}：${rowPrice(row)}`).join("；"):"暂无 D 级历史基准"}</p>
            </article>
            <article>
              <b>邻国参考</b>
              <p>{neighborRows.length?neighborRows.map(row=>`${row.platform_name}：${rowPrice(row)}`).join("；"):"暂无 E 级邻国参考"}</p>
            </article>
            <article>
              <b>渠道清单</b>
              <p>
                {channels.length
                  ? channels.join("、")
                  : configuredChannels.length?configuredChannels.join("、"):"渠道清单采集中：当地主要商超、电商平台与农贸市场"}
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
