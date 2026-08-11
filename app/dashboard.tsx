"use client";

import { useEffect, useMemo, useState } from "react";
import {
  countryOptions,
  countrySummaries,
  dataSources,
  mirrorRecords,
  opportunities,
  priceObservations,
  tradeRecords,
  type CountryCode,
  type Opportunity,
} from "./data";

const navigation = [
  { id: "overview", label: "指挥台", mark: "01" },
  { id: "mirror", label: "贸易交叉", mark: "02" },
  { id: "opportunities", label: "商机雷达", mark: "03" },
  { id: "prices", label: "价格渠道", mark: "04" },
  { id: "sources", label: "数据资产", mark: "05" },
];

function compactCurrency(value: number | null) {
  if (value === null) return "待补报";
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(2)}M`;
  if (value >= 1_000) return `$${Math.round(value / 1_000)}K`;
  return `$${value.toLocaleString("zh-CN")}`;
}

function fullCurrency(value: number | null) {
  return value === null ? "—" : `$${value.toLocaleString("en-US")}`;
}

function percent(value: number | null, withSign = true) {
  if (value === null) return "—";
  return `${withSign && value > 0 ? "+" : ""}${value.toFixed(1)}%`;
}

function mirrorMetrics(importerCifUsd: number | null, chinaFobUsd: number) {
  if (importerCifUsd === null) {
    return { gap: null, delta: null, status: "待补报", tone: "neutral" };
  }
  const delta = importerCifUsd - chinaFobUsd;
  const gap = (Math.abs(delta) / Math.max(importerCifUsd, chinaFobUsd)) * 100;
  if (Math.max(importerCifUsd, chinaFobUsd) < 50_000) {
    return { gap, delta, status: "低基数", tone: "neutral" };
  }
  if (gap <= 15) return { gap, delta, status: "基本一致", tone: "good" };
  if (gap <= 30) return { gap, delta, status: "轻微偏差", tone: "watch" };
  if (gap <= 50) return { gap, delta, status: "需复核", tone: "watch" };
  return { gap, delta, status: "显著异常", tone: "alert" };
}

function jumpTo(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function ScoreRing({ score }: { score: number }) {
  const color = score >= 75 ? "var(--lime)" : score >= 60 ? "var(--gold)" : "var(--clay)";
  return (
    <div
      className="score-ring"
      style={{ background: `conic-gradient(${color} ${score * 3.6}deg, rgba(255,255,255,.12) 0deg)` }}
      aria-label={`机会分 ${score}`}
    >
      <span>{score}</span>
    </div>
  );
}

function OpportunityDrawer({ item, onClose }: { item: Opportunity; onClose: () => void }) {
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => event.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="drawer-backdrop">
      <button className="drawer-backdrop-close" onClick={onClose} aria-label="关闭机会详情" />
      <section
        className="drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="drawer-title"
      >
        <button className="drawer-close" onClick={onClose} aria-label="关闭详情">×</button>
        <div className="eyebrow">OPPORTUNITY FILE / {item.hs}</div>
        <div className="drawer-heading">
          <div>
            <p>{item.country}</p>
            <h2 id="drawer-title">{item.product}</h2>
          </div>
          <ScoreRing score={item.score} />
        </div>
        <div className="drawer-badges">
          <span className="pill pill-gold">{item.status}</span>
          <span className="pill">评分覆盖 {item.coverage}%</span>
          <span className="pill">证据 {item.confidence}</span>
        </div>
        <div className="drawer-signal">
          <span>核心信号</span>
          <p>{item.signal}</p>
        </div>
        <div className="metric-stack">
          {item.metrics.map((metric) => (
            <div className="metric-row" key={metric.label}>
              <div className="metric-copy">
                <strong>{metric.label}</strong>
                <small>{metric.note}</small>
              </div>
              <div className="metric-visual">
                <span>{metric.value === null ? "待补" : metric.value}</span>
                <div className="metric-track">
                  <i style={{ width: `${metric.value ?? 0}%` }} />
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="next-action">
          <span>下一步验证</span>
          <p>{item.nextAction}</p>
        </div>
        <p className="drawer-note">机会分用于发现市场信号，不构成收入预测、投资评级或收益承诺。</p>
      </section>
    </div>
  );
}

export default function Dashboard() {
  const [country, setCountry] = useState<CountryCode>("ALL");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Opportunity | null>(null);
  const [briefReady, setBriefReady] = useState(false);

  const visibleTrade = useMemo(() => {
    const query = search.trim().toLowerCase();
    return tradeRecords.filter((record) => {
      const countryMatch = country === "ALL" || record.countryCode === country;
      const queryMatch = !query || `${record.country}${record.product}${record.hs}`.toLowerCase().includes(query);
      return countryMatch && queryMatch;
    });
  }, [country, search]);

  const visibleMirrors = mirrorRecords.filter((record) => country === "ALL" || record.countryCode === country);
  const visibleOpportunities = opportunities.filter((item) => country === "ALL" || item.countryCode === country);
  const visiblePrices = priceObservations.filter((item) => country === "ALL" || item.countryCode === country);
  const totalTrade = visibleTrade.reduce((sum, record) => sum + (record.y2024 ?? 0), 0);
  const alertCount = visibleMirrors.filter((record) => mirrorMetrics(record.importerCifUsd, record.chinaFobUsd).tone === "alert").length;
  const selectedLabel = countryOptions.find((item) => item.code === country)?.label ?? "中亚五国";

  const runBrief = () => {
    setBriefReady(true);
    jumpTo("brief");
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <button className="brand" onClick={() => jumpTo("overview")} aria-label="返回顶部">
          <span className="brand-seal">枢</span>
          <span><strong>因恒数智</strong><small>KASHGAR GATEWAY</small></span>
        </button>
        <nav aria-label="主要导航">
          {navigation.map((item) => (
            <button key={item.id} onClick={() => jumpTo(item.id)}>
              <span>{item.mark}</span>{item.label}
            </button>
          ))}
        </nav>
        <div className="sidebar-spacer" />
        <div className="side-status">
          <span className="pulse-dot" />
          <div><strong>基线运行中</strong><small>数据核验日 2026-08-10</small></div>
        </div>
        <div className="coverage-box">
          <span>情报覆盖</span>
          <strong>5国 · 9组贸易 · 7条价格</strong>
          <small>首版基线，非实时行情</small>
        </div>
      </aside>

      <main>
        <header className="topbar">
          <div className="mobile-brand"><span>枢</span> 因恒数智</div>
          <label className="search-box">
            <span>⌕</span>
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="搜索国家、商品或 HS 编码"
              aria-label="搜索国家、商品或HS编码"
            />
            {search && <button onClick={() => setSearch("")} aria-label="清除搜索">×</button>}
          </label>
          <div className="top-actions">
            <span className="baseline-tag"><i /> 基线已核验</span>
            <button className="button button-dark" onClick={runBrief}>{briefReady ? "简报已更新" : "生成合作方简报"}</button>
          </div>
        </header>

        <div className="content-wrap">
          <section className="hero" id="overview">
            <div className="hero-copy">
              <div className="eyebrow">CHINA × KASHGAR × CENTRAL ASIA</div>
              <h1>从喀什，<br />看见中亚贸易机会。</h1>
              <p>把分散的官方贸易、市场价格、渠道与项目数据，转化成可验证的商机、合作方简报与 AI 内容。</p>
              <div className="hero-actions">
                <button className="button button-lime" onClick={() => jumpTo("opportunities")}>查看机会雷达 <span>↗</span></button>
                <button className="button button-ghost" onClick={() => jumpTo("mirror")}>检查贸易信息差</button>
              </div>
            </div>
            <div className="corridor-card" aria-label="中国经喀什连接中亚五国的贸易走廊示意">
              <div className="corridor-head">
                <span>贸易走廊 / TRADE CORRIDOR</span>
                <b>5国覆盖</b>
              </div>
              <div className="corridor-map">
                <div className="route-line route-a" />
                <div className="route-line route-b" />
                <div className="route-line route-c" />
                <div className="route-line route-d" />
                <div className="route-line route-e" />
                <div className="node node-china"><small>供给端</small><strong>中国</strong></div>
                <div className="node node-kashgar"><span>枢纽</span><strong>喀什</strong><small>KASHGAR</small></div>
                <div className="node node-kz"><i />哈萨克斯坦</div>
                <div className="node node-uz"><i />乌兹别克斯坦</div>
                <div className="node node-kg"><i />吉尔吉斯斯坦</div>
                <div className="node node-tj"><i />塔吉克斯坦</div>
                <div className="node node-tm"><i />土库曼斯坦</div>
              </div>
              <div className="corridor-foot">
                <span><i className="legend-live" /> 已有公开数据</span>
                <span><i className="legend-gap" /> 待补口岸数据</span>
              </div>
            </div>
          </section>

          <section className="stat-grid" aria-label="关键指标">
            <article><span>2024重点菌类进口</span><strong>{compactCurrency(totalTrade)}</strong><small>{selectedLabel} · 当前筛选口径</small></article>
            <article><span>贸易数据记录</span><strong>{visibleTrade.length}<em>组</em></strong><small>2022—2024 年基线</small></article>
            <article><span>高优先机会</span><strong>{visibleOpportunities.filter((item) => item.score >= 65).length}<em>项</em></strong><small>评分覆盖度需同时查看</small></article>
            <article className={alertCount ? "stat-alert" : ""}><span>镜像异常</span><strong>{alertCount}<em>项</em></strong><small>进口CIF vs 中国出口FOB</small></article>
          </section>

          <section className="country-section">
            <div className="section-heading compact-heading">
              <div><div className="eyebrow">MARKET LENS</div><h2>按国家切换情报视角</h2></div>
              <p>所有金额均为美元；缺失值不按零处理。</p>
            </div>
            <div className="country-tabs" role="tablist" aria-label="国家筛选">
              {countryOptions.map((item) => (
                <button
                  key={item.code}
                  role="tab"
                  aria-selected={country === item.code}
                  className={country === item.code ? "active" : ""}
                  onClick={() => setCountry(item.code)}
                >{item.short}</button>
              ))}
            </div>
          </section>

          <section className="panel-grid" id="brief">
            <article className="panel market-panel">
              <div className="panel-title">
                <div><span>五国市场结构</span><h3>重点菌类进口额</h3></div>
                <small>UN Comtrade · 2024</small>
              </div>
              <div className="market-list">
                {countrySummaries.map((item, index) => (
                  <button key={item.code} onClick={() => setCountry(item.code)} className={country === item.code ? "selected" : ""}>
                    <span className="rank">0{index + 1}</span>
                    <span className="market-name"><strong>{item.country}</strong><small>{item.state}</small></span>
                    <span className="bar-wrap"><i style={{ width: `${item.share}%` }} /></span>
                    <span className="market-value"><strong>{compactCurrency(item.value)}</strong><small className={(item.change ?? 0) < 0 ? "negative" : "positive"}>{percent(item.change)}</small></span>
                  </button>
                ))}
              </div>
            </article>

            <article className={`panel brief-panel ${briefReady ? "is-ready" : ""}`}>
              <div className="panel-title">
                <div><span>AI 情报摘要</span><h3>{selectedLabel} · 本周信号</h3></div>
                <small>{briefReady ? "刚刚生成" : "基线生成"}</small>
              </div>
              <ol className="brief-list">
                <li><b>01</b><div><strong>吉国其他鲜蘑菇进入高增长区间</strong><p>2024进口额53.6万美元，同比+117.8%；先补批发价格与来源国。</p></div></li>
                <li><b>02</b><div><strong>哈国加工菌镜像差异需要复核</strong><p>两侧差异72.1%，可能涉及HS版本、转口或CIF/FOB口径。</p></div></li>
                <li><b>03</b><div><strong>哈国鲜双孢菇适合优先验证冷链</strong><p>进口依赖粗估较高，已观察到多个稳定挂牌价格带。</p></div></li>
              </ol>
              <button className="text-button" onClick={() => jumpTo("opportunities")}>打开完整机会清单 <span>→</span></button>
            </article>
          </section>

          <section className="section-block" id="mirror">
            <div className="section-heading">
              <div><div className="eyebrow">MIRROR CHECK</div><h2>中国出口 × 中亚进口交叉核验</h2></div>
              <p>镜像差异只用于发现口径和链路问题；正负方向不代表利好或利空。</p>
            </div>
            <div className="mirror-table" role="table" aria-label="贸易镜像差异表">
              <div className="table-head" role="row">
                <span>市场 / 商品</span><span>进口方申报 CIF</span><span>中国出口镜像 FOB</span><span>差异率</span><span>状态</span>
              </div>
              {visibleMirrors.map((record) => {
                const metrics = mirrorMetrics(record.importerCifUsd, record.chinaFobUsd);
                return (
                  <div className="table-row" role="row" key={`${record.countryCode}-${record.hs}`}>
                    <span className="product-cell"><strong>{record.country}</strong><small>HS {record.hs} · {record.product}</small></span>
                    <span data-label="进口方 CIF">{fullCurrency(record.importerCifUsd)}</span>
                    <span data-label="中国出口 FOB">{fullCurrency(record.chinaFobUsd)}</span>
                    <span className="gap-cell" data-label="镜像差异率">
                      <strong>{metrics.gap === null ? "—" : `${metrics.gap.toFixed(1)}%`}</strong>
                      <i><b style={{ width: `${metrics.gap ?? 0}%` }} /></i>
                    </span>
                    <span data-label="状态"><em className={`status-dot ${metrics.tone}`}>{metrics.status}</em></span>
                  </div>
                );
              })}
              {visibleMirrors.length === 0 && <div className="empty-state">当前筛选没有可比镜像记录，已加入补数队列。</div>}
            </div>
            <div className="method-note"><span>口径说明</span><p>差异率 = |进口方CIF − 中国出口FOB| ÷ 两者较大值。任一侧缺失时显示“待补报”，不会把缺失值当作0。</p></div>
          </section>

          <section className="section-block dark-section" id="opportunities">
            <div className="section-heading light-heading">
              <div><div className="eyebrow">OPPORTUNITY RADAR</div><h2>可解释的市场机会评分</h2></div>
              <p>综合市场规模、增长动能、进口依赖、拓展空间、价差和渠道；缺失项按可用权重重算。</p>
            </div>
            <div className="opportunity-grid">
              {visibleOpportunities.map((item, index) => (
                <button className="opportunity-card" key={item.id} onClick={() => setSelected(item)}>
                  <div className="opp-top"><span>0{index + 1}</span><div className="opp-score"><strong>{item.score}</strong><small>/100</small></div></div>
                  <div className="opp-place">{item.country} · HS {item.hs}</div>
                  <h3>{item.product}</h3>
                  <div className="opp-data"><span><small>市场规模</small><strong>{compactCurrency(item.marketUsd)}</strong></span><span><small>同比变化</small><strong className={item.change < 0 ? "negative" : "positive"}>{percent(item.change)}</strong></span></div>
                  <p>{item.signal}</p>
                  <div className="opp-foot"><span>{item.status}</span><span>覆盖 {item.coverage}% · 证据 {item.confidence} <b>↗</b></span></div>
                </button>
              ))}
              {visibleOpportunities.length === 0 && <div className="dark-empty">该市场暂不出总分：当前评分覆盖度不足40%。</div>}
            </div>
          </section>

          <section className="section-block" id="prices">
            <div className="section-heading">
              <div><div className="eyebrow">PRICE & CHANNEL</div><h2>市场挂牌价与渠道观察</h2></div>
              <p>挂牌价不等于成交价；所有观察均保留规格、日期和来源。</p>
            </div>
            <div className="price-layout">
              <div className="price-table">
                <div className="price-head"><span>市场</span><span>商品 / 渠道</span><span>挂牌价</span><span>采集</span></div>
                {visiblePrices.map((item, index) => (
                  <div className="price-row" key={`${item.city}-${item.product}-${index}`}>
                    <span><strong>{item.city}</strong><small>{item.countryCode}</small></span>
                    <span><strong>{item.product}</strong><small>{item.channel}</small></span>
                    <span className="price-value">{item.price}</span>
                    <span><strong>{item.date}</strong><small>{item.source}</small></span>
                  </div>
                ))}
                {visiblePrices.length === 0 && <div className="empty-state">该市场还没有完成价格核验。</div>}
              </div>
              <aside className="collection-card">
                <span className="collection-index">NEXT / 01</span>
                <div className="collection-icon">↕</div>
                <h3>下一批应补的数据</h3>
                <ul><li>实际批发成交价与采购量</li><li>喀什—中亚冷链线路报价</li><li>进口商联系人与采购周期</li><li>口岸通关时长及异常原因</li></ul>
                <button onClick={runBrief}>加入合作方采集清单 <span>＋</span></button>
              </aside>
            </div>
          </section>

          <section className="section-block" id="sources">
            <div className="section-heading">
              <div><div className="eyebrow">DATA FOUNDATION</div><h2>数据源、等级与接入状态</h2></div>
              <p>官方统计构成主表，市场观察构成证据层；两者不混写。</p>
            </div>
            <div className="source-grid">
              {dataSources.map((source) => (
                <a className="source-card" key={source.name} href={source.url} target={source.url.startsWith("http") ? "_blank" : undefined} rel="noreferrer">
                  <div className="source-top"><strong>{source.name}</strong><span>{source.level}</span></div>
                  <div className="source-meta"><span>{source.scope}</span><span>{source.cadence}</span></div>
                  <p>{source.note}</p>
                  <div className="source-status"><i />{source.status}<b>↗</b></div>
                </a>
              ))}
            </div>
          </section>

          <section className="distribution-section">
            <div><div className="eyebrow">AI DISTRIBUTION</div><h2>一份结构化数据，生成一整套对外内容。</h2></div>
            <div className="distribution-flow">
              {[
                ["01", "可信数据", "来源与口径可追溯"],
                ["02", "图表看报", "周报与机会卡片"],
                ["03", "视频脚本", "钩子、口播与分镜"],
                ["04", "数字形象", "多语种数字人视频"],
                ["05", "自动分发", "内容表现与线索回流"],
              ].map(([number, title, copy], index) => (
                <div className="flow-item" key={number}><span>{number}</span><strong>{title}</strong><small>{copy}</small>{index < 4 && <i>→</i>}</div>
              ))}
            </div>
          </section>

          <footer>
            <div><span className="brand-seal small">枢</span><strong>因恒数智 · 中亚农业贸易情报</strong></div>
            <p>公开数据用于市场研究与内容生产参考，不构成贸易决策或投资建议。</p>
            <span>BASELINE / 2026-08-10</span>
          </footer>
        </div>
      </main>
      {selected && <OpportunityDrawer item={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
