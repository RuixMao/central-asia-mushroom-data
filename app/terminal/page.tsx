"use client";

import Image from "next/image";
import Link from "next/link";
import { useMemo, useState } from "react";

type Country = "ALL" | "KZ" | "UZ" | "KG" | "TJ" | "TM";

const countries: { code: Country; label: string }[] = [
  { code: "ALL", label: "全部市场" }, { code: "KZ", label: "哈萨克斯坦" },
  { code: "UZ", label: "乌兹别克斯坦" }, { code: "KG", label: "吉尔吉斯斯坦" },
  { code: "TJ", label: "塔吉克斯坦" }, { code: "TM", label: "土库曼斯坦" },
];

const trade = [
  { country: "KZ", name: "哈萨克斯坦", hs: "070951", product: "鲜、冷双孢蘑菇", y2022: 8893873, y2023: 3181278, y2024: 4193266, weight: 3489, quality: "已核验" },
  { country: "KZ", name: "哈萨克斯坦", hs: "200310", product: "加工保藏蘑菇", y2022: 4412358, y2023: 1644872, y2024: 1027970, weight: null, quality: "待复核" },
  { country: "KZ", name: "哈萨克斯坦", hs: "070959", product: "其他鲜蘑菇", y2022: 510974, y2023: 426093, y2024: 409221, weight: 526, quality: "已核验" },
  { country: "UZ", name: "乌兹别克斯坦", hs: "070951", product: "鲜、冷双孢蘑菇", y2022: 15930, y2023: 488375, y2024: 456804, weight: 197, quality: "已核验" },
  { country: "UZ", name: "乌兹别克斯坦", hs: "200310", product: "加工保藏蘑菇", y2022: 69233, y2023: 111800, y2024: 68204, weight: null, quality: "待复核" },
  { country: "KG", name: "吉尔吉斯斯坦", hs: "070951", product: "鲜、冷双孢蘑菇", y2022: 9994, y2023: 40966, y2024: 40376, weight: 24, quality: "待复核" },
  { country: "KG", name: "吉尔吉斯斯坦", hs: "070959", product: "其他鲜蘑菇", y2022: 97554, y2023: 246088, y2024: 535916, weight: null, quality: "待复核" },
  { country: "KG", name: "吉尔吉斯斯坦", hs: "200310", product: "加工保藏蘑菇", y2022: 130482, y2023: 130030, y2024: 228842, weight: 46, quality: "待复核" },
  { country: "TJ", name: "塔吉克斯坦", hs: "200310", product: "加工保藏蘑菇", y2022: 39358, y2023: 119104, y2024: null, weight: null, quality: "缺失" },
];

const readyAssets = [
  { title: "UN Comtrade 菌类贸易", coverage: "中亚五国 · 3类HS · 2022–2024", cadence: "年度 / 可扩展月度", state: "已接入", value: "市场规模、增长、来源国、镜像差异", url: "https://uncomtrade.org/docs/un-comtrade-api/" },
  { title: "乌兹别克斯坦食用菌产量", coverage: "全国及14个地区 · 2018–2024", cadence: "年度", state: "已发现", value: "本地产能、进口依赖、区域生产地图", url: "https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_519.pdf" },
  { title: "FAOSTAT 农业生产与贸易", coverage: "中亚五国 · 长时间序列", cadence: "年度", state: "待批量接入", value: "供需基线、品类替代、跨国比较", url: "https://www.fao.org/faostat/en/" },
  { title: "哈萨克斯坦官方农业统计", coverage: "国家 / 地区 · 农业与设施生产", cadence: "月度 / 年度", state: "目录已定位", value: "本地产量、设施农业和区域供给", url: "https://stat.gov.kz/en/industries/businessstatistics/stat-forrest-village-hunt-fish/dynamic-tables/" },
];

const signalAssets = [
  { priority: 1, title: "进口商与经销商图谱", fields: "企业、品牌、城市、渠道、采购品类、联系方式、最近活动", method: "海关线索 + 企业网站 + 商超商品页 + 展会名录", product: "买家数据库 / 销售线索", score: 94 },
  { priority: 2, title: "真实批发价与采购需求", fields: "规格、产地、数量、成交价、账期、交付地、采购周期", method: "本地批发市场、Telegram/WhatsApp群、合作方报价", product: "采购价格指数 / 周报", score: 92 },
  { priority: 3, title: "喀什—中亚冷链成本", fields: "路线、车型、温层、报价、时效、损耗、口岸等待", method: "物流商询价 + 司机访谈 + 口岸运行记录", product: "到岸成本计算器", score: 90 },
  { priority: 4, title: "设施农业项目雷达", fields: "项目、业主、投资额、产能、设备需求、建设阶段、联系人", method: "政府公告 + 招标 + 园区 + 企业新闻 + 招聘", product: "项目订阅 / 商机预警", score: 87 },
  { priority: 5, title: "零售商品与品牌监测", fields: "SKU、品牌、规格、价格、促销、门店、库存状态", method: "电商与商超定点采集，保留页面证据", product: "渠道与品牌监测", score: 82 },
  { priority: 6, title: "产能与原料约束", fields: "菇房面积、日产能、菌种、基质、能源、水、设备来源", method: "企业访谈 + 招聘 + 设备商 + 卫星/园区线索", product: "供应能力评估", score: 78 },
];

const usd = (value: number | null) => value === null ? "未报告" : new Intl.NumberFormat("zh-CN", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);

export default function TerminalPage() {
  const [country, setCountry] = useState<Country>("ALL");
  const [view, setView] = useState<"market" | "assets">("market");
  const rows = useMemo(() => country === "ALL" ? trade : trade.filter(item => item.country === country), [country]);
  const total = rows.reduce((sum, row) => sum + (row.y2024 ?? 0), 0);
  const verified = rows.filter(row => row.quality === "已核验").length;
  const max = Math.max(...rows.map(row => row.y2024 ?? 0), 1);

  return <div className="intel-app">
    <aside className="intel-side">
      <Link href="/" className="intel-brand"><Image src="/inhen-tech-logo.png" alt="因恒科技" width={282} height={90} priority /></Link>
      <div className="intel-product"><span>YINHENG INTELLIGENCE</span><strong>中亚菌类数据终端</strong><small>RESEARCH PREVIEW · 01</small></div>
      <nav><button className={view === "market" ? "active" : ""} onClick={() => setView("market")}><i>01</i>市场看板</button><button className={view === "assets" ? "active" : ""} onClick={() => setView("assets")}><i>02</i>数据资产地图</button><Link href="/market-data"><i>03</i>公开数据页</Link><Link href="/#contact"><i>04</i>申请完整数据</Link></nav>
      <div className="intel-side-note"><b>数据原则</b><p>来源可追溯、缺失不填零、官方数据与商业采集分层管理。</p></div>
    </aside>
    <main className="intel-main">
      <header className="intel-top"><div><span>中亚五国 / 菌类产业</span><b>{view === "market" ? "市场概览" : "数据资产与采集路线"}</b></div><div className="freshness"><i /> 数据基线更新至 2026-08-11</div></header>

      {view === "market" ? <>
        <section className="intel-hero"><div><span>MARKET BASELINE</span><h1>先用已有数据建立事实底座</h1><p>当前看板整合重点菌类贸易记录，并明确标记已核验、待复核和缺失数据。下一步将扩展月度、伙伴国和数量口径。</p></div><div className="country-switch">{countries.map(item => <button key={item.code} className={country === item.code ? "active" : ""} onClick={() => setCountry(item.code)}>{item.label}</button>)}</div></section>
        <section className="intel-kpis"><article><span>2024 已报告进口额</span><strong>{usd(total)}</strong><small>当前筛选口径</small></article><article><span>贸易序列</span><strong>{rows.length}</strong><small>国家 × HS 编码</small></article><article><span>已核验记录</span><strong>{verified}</strong><small>已通过官方接口复核</small></article><article><span>待补数据</span><strong>{rows.filter(row => row.y2024 === null).length}</strong><small>不以 0 替代缺失</small></article></section>
        <section className="intel-grid"><article className="intel-panel intel-chart"><div className="intel-panel-head"><div><span>2024 IMPORT VALUE</span><h2>市场与品类结构</h2></div><small>UN Comtrade · USD</small></div><div className="intel-bars">{rows.map(row => <div key={row.country + row.hs}><span><b>{row.name}</b><small>HS {row.hs} · {row.product}</small></span><i><em style={{ width: `${((row.y2024 ?? 0) / max) * 100}%` }} /></i><strong>{usd(row.y2024)}</strong></div>)}</div></article><article className="intel-panel production-card"><div className="intel-panel-head"><div><span>LOCAL PRODUCTION</span><h2>乌兹别克斯坦产量信号</h2></div><small>官方统计 · 千吨</small></div><div className="production-number"><strong>0.3</strong><span>2024年全国食用菌产量</span></div><div className="production-regions"><span><b>撒马尔罕</b>0.1</span><span><b>苏尔汉河</b>0.1</span><span><b>塔什干州</b>0.1</span></div><p>官方序列显示2023年为0.1千吨、2024年为0.3千吨；进口与本地产量联合观察，比单看贸易额更接近真实供需。</p><a href="https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_519.pdf" target="_blank" rel="noreferrer">查看原始数据 →</a></article></section>
        <section className="intel-table-panel"><div className="intel-panel-head"><div><span>TRACEABLE RECORDS</span><h2>贸易数据明细</h2></div><small>数值保留原始美元口径</small></div><div className="intel-table"><div className="intel-row head"><span>市场 / 商品</span><span>2022</span><span>2023</span><span>2024</span><span>数量</span><span>质量</span></div>{rows.map(row => <div className="intel-row" key={row.country + row.hs}><span><b>{row.name}</b><small>HS {row.hs} · {row.product}</small></span><span>{usd(row.y2022)}</span><span>{usd(row.y2023)}</span><span>{usd(row.y2024)}</span><span>{row.weight ? `${row.weight.toLocaleString()} 吨` : "待补"}</span><span><em className={`quality ${row.quality === "已核验" ? "ok" : row.quality === "缺失" ? "missing" : "review"}`}>{row.quality}</em></span></div>)}</div></section>
      </> : <>
        <section className="intel-hero asset-hero"><div><span>DATA ASSET MAP</span><h1>把公开数据变成独家商业资产</h1><p>公开数据解决“市场发生了什么”，持续采集的数据解决“客户应该联系谁、成本是多少、机会什么时候发生”。</p></div><div className="asset-summary"><strong>4</strong><span>可直接接入的权威数据源</span><strong>6</strong><span>优先建设的商业数据产品</span></div></section>
        <section className="asset-section"><div className="asset-title"><span>01 / AVAILABLE DATA</span><h2>已有数据与接入状态</h2></div><div className="ready-grid">{readyAssets.map(asset => <a href={asset.url} target="_blank" rel="noreferrer" key={asset.title}><div><strong>{asset.title}</strong><em>{asset.state}</em></div><p>{asset.coverage}</p><span>{asset.cadence}</span><b>商业用途：{asset.value}</b></a>)}</div></section>
        <section className="asset-section dark-assets"><div className="asset-title"><span>02 / PROPRIETARY SIGNALS</span><h2>值得持续采集的高价值数据</h2><p>这些数据没有完整现成 dataset，采集、验证和更新能力本身就是产品壁垒。</p></div><div className="signal-list">{signalAssets.map(asset => <article key={asset.title}><span>0{asset.priority}</span><div><h3>{asset.title}</h3><p>{asset.fields}</p><small>采集：{asset.method}</small></div><div><strong>{asset.score}</strong><small>商业价值分</small><b>{asset.product}</b></div></article>)}</div></section>
        <section className="collection-plan"><div><span>90-DAY COLLECTION PLAN</span><h2>第一阶段采集顺序</h2></div><ol><li><b>01</b><span>补齐五国贸易月度数据与伙伴国结构</span><em>可自动化</em></li><li><b>02</b><span>建立100家进口商、经销商和零售渠道名录</span><em>半自动 + 人工核验</em></li><li><b>03</b><span>每周采集阿拉木图、比什凯克、塔什干价格</span><em>持续监测</em></li><li><b>04</b><span>建立喀什出发冷链报价与通关时效样本</span><em>合作方采集</em></li></ol></section>
      </>}
    </main>
  </div>;
}
