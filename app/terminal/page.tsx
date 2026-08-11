"use client";
import Link from "next/link";
import { useState } from "react";
import MarketPanel from "./market-panel";

const readyAssets = [
  { title:"UN Comtrade 菌类贸易", coverage:"中亚五国 · 3类HS · 年度与月度", cadence:"年度 / 月度", state:"实时接入", value:"市场规模、增长、来源国、镜像差异", url:"https://uncomtrade.org/docs/un-comtrade-api/" },
  { title:"乌兹别克斯坦食用菌产量", coverage:"全国及14个地区 · 2018–2024", cadence:"年度", state:"已发现", value:"本地产能、进口依赖、区域生产地图", url:"https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_519.pdf" },
  { title:"FAOSTAT 农业生产与贸易", coverage:"中亚五国 · 长时间序列", cadence:"年度", state:"待批量接入", value:"供需基线、品类替代、跨国比较", url:"https://www.fao.org/faostat/en/" },
  { title:"日度价格观察", coverage:"阿拉木图 / 塔什干 · 重点菌类", cadence:"日度采集", state:"样例接入", value:"价格趋势、渠道差异、异常预警", url:"/market-data" },
];
const signals = [[1,"进口商与经销商图谱","企业、品牌、城市、渠道、采购品类、联系方式","买家数据库 / 销售线索",94],[2,"真实批发价与采购需求","规格、产地、数量、成交价、账期、交付地","采购价格指数 / 周报",92],[3,"喀什—中亚冷链成本","路线、车型、温层、报价、时效、损耗","到岸成本计算器",90],[4,"设施农业项目雷达","项目、业主、投资额、产能、设备需求、建设阶段","项目订阅 / 商机预警",87]];

export default function TerminalPage(){
  const [view,setView]=useState<"market"|"assets">("market");
  const [liveState,setLiveState]=useState<"loading"|"live"|"fallback">("loading");
  return <div className="intel-app"><aside className="intel-side"><Link href="/" className="intel-brand"><img src="/inhen-tech-logo.png" alt="因恒科技" width="282" height="90" /></Link><div className="intel-product"><span>YINHENG INTELLIGENCE</span><strong>中亚菌类数据终端</strong><small>CONTINUOUS DATA · 02</small></div><nav><button className={view==="market"?"active":""} onClick={()=>setView("market")}><i>01</i>连续数据看板</button><button className={view==="assets"?"active":""} onClick={()=>setView("assets")}><i>02</i>数据资产地图</button><Link href="/market-data"><i>03</i>公开数据页</Link><Link href="/#contact"><i>04</i>申请完整数据</Link></nav><div className="intel-side-note"><b>数据原则</b><p>来源可追溯、缺失不填零、年度/月度/日度分层管理。</p></div></aside><main className="intel-main"><header className="intel-top"><div><span>中亚五国 / 菌类产业</span><b>{view==="market"?"连续数据看板":"数据资产与采集路线"}</b></div><div className={`freshness ${liveState}`}><i />{liveState==="live"?"最新数据已连接":liveState==="loading"?"正在同步官方数据":"显示已验证基线"}</div></header>{view==="market"?<MarketPanel onState={setLiveState}/>:<><section className="intel-hero asset-hero"><div><span>DATA ASSET MAP</span><h1>把公开数据变成连续商业资产</h1><p>贸易统计回答市场规模，月度序列捕捉变化，日度采集补足价格和渠道信号。</p></div><div className="asset-summary"><strong>3</strong><span>年度 / 月度 / 日度数据层</span><strong>5</strong><span>持续覆盖的中亚国家</span></div></section><section className="asset-section"><div className="asset-title"><span>01 / AVAILABLE DATA</span><h2>已有数据与接入状态</h2></div><div className="ready-grid">{readyAssets.map(asset=><a href={asset.url} target={asset.url.startsWith("http")?"_blank":undefined} rel="noreferrer" key={asset.title}><div><strong>{asset.title}</strong><em>{asset.state}</em></div><p>{asset.coverage}</p><span>{asset.cadence}</span><b>商业用途：{asset.value}</b></a>)}</div></section><section className="asset-section dark-assets"><div className="asset-title"><span>02 / PROPRIETARY SIGNALS</span><h2>下一阶段持续采集</h2></div><div className="signal-list">{signals.map(([priority,title,fields,product,score])=><article key={String(title)}><span>0{priority}</span><div><h3>{title}</h3><p>{fields}</p></div><div><strong>{score}</strong><small>商业价值分</small><b>{product}</b></div></article>)}</div></section></>}</main></div>;
}
