import Link from "next/link";
import ProductShell from "../product-shell";
import { datasets } from "../saas-data";

export default function CatalogPage(){return <ProductShell><main className="saas-main"><section className="saas-hero compact"><span>DATA CATALOG / 06 DATASETS</span><h1>把中亚菌类市场，拆成可查询的数据资产</h1><p>贸易、价格、物流、买家和准入标准统一口径管理。每条记录保留来源、采集时间和证据状态。</p></section><section className="filter-bar"><b>全部数据</b><span>贸易</span><span>价格</span><span>物流</span><span>企业</span><span>标准</span><small>最近更新：2026-08-11</small></section><section className="dataset-grid">{datasets.map((item,i)=><article key={item.slug}><div><span>0{i+1} / {item.category}</span><em>{item.frequency}</em></div><h2>{item.name}</h2><p>{item.value}</p><dl><div><dt>覆盖</dt><dd>{item.countries}</dd></div><div><dt>记录</dt><dd>{item.records}</dd></div><div><dt>更新</dt><dd>{item.updated}</dd></div></dl><Link href={`/dataset/${item.slug}`}>查看样本与字段 <b>→</b></Link></article>)}</section></main></ProductShell>}
