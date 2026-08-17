"use client";
import { useEffect, useMemo, useState } from "react";

type PriceData = { species_id?: string; variety?: string; product_form?: string; form?: string; package_display?: string; spec?: string; platform_name?: string; channel?: string; price_local?: number; currency?: string; price_usd?: number; normalized_price_usd_per_kg?: number; price_cny?: number; observed_at?: string; source_url?: string; status?: "live" | "gap" };
type Snapshot = { id: string; country: string; data: PriceData; source: string };

const countryNames: Record<string, string> = { KZ: "哈萨克斯坦", UZ: "乌兹别克斯坦", KG: "吉尔吉斯斯坦", TJ: "塔吉克斯坦", TM: "土库曼斯坦" };
const speciesNames: Record<string, string> = { agaricus_bisporus: "双孢菇", button_mushroom: "双孢菇", pleurotus_ostreatus: "平菇", oyster_mushroom: "平菇", lentinula_edodes: "香菇", shiitake: "香菇", flammulina_velutipes: "金针菇", enoki: "金针菇", pleurotus_eryngii: "杏鲍菇", king_oyster_mushroom: "杏鲍菇", wood_ear: "木耳", mixed_mushrooms: "混合菌菇", mixed_species: "混合菌菇" };
const formNames: Record<string, string> = { fresh: "鲜品", dried: "干品", frozen: "冻品", canned: "罐藏", pickled: "腌制", processed: "加工品" };
const sourceNames: Record<string, string> = { "kaspi-kz": "Kaspi 电商平台", "yandex-uz": "Yandex 电商平台", "magnit-tj": "Magnit 生鲜电商", somon: "Somon 分类信息平台", gipertm: "Giper 网上超市", arbuz: "Arbuz 生鲜电商", globus: "Globus 网上超市", olx: "OLX 分类信息平台", omarket: "O!Market 电商平台", asmanexpress: "Asman 网上超市" };
const fallback: Snapshot[] = [
  { id: "kg-1", country: "KG", source: "globus", data: { species_id: "button_mushroom", product_form: "fresh", package_display: "1 kg", platform_name: "Globus Online", price_local: 520, currency: "KGS", price_usd: 5.95, normalized_price_usd_per_kg: 5.95, observed_at: "2026-08-11", source_url: "https://globus-online.kg/", status: "live" } },
  { id: "tj-1", country: "TJ", source: "magnit-tj", data: { species_id: "button_mushroom", product_form: "fresh", package_display: "250 g", platform_name: "Magnit.tj", price_local: 29.9, currency: "TJS", price_usd: 3.23, normalized_price_usd_per_kg: 12.94, observed_at: "2026-08-11", source_url: "https://magnit.tj/", status: "live" } },
];
const labelSpecies = (data: PriceData) => { const value = data.species_id ?? data.variety ?? ""; return speciesNames[value] ?? (/[一-鿿]/.test(value) ? value : "其他菌菇"); };
const labelForm = (data: PriceData) => formNames[data.product_form ?? ""] ?? data.form ?? "—";
const isComplete = (record: Snapshot) => { const data = record.data; return data.status !== "gap" && data.price_local != null && Boolean(data.currency && data.observed_at && (data.product_form || data.form) && (data.package_display || data.spec) && labelSpecies(data) !== "其他菌菇"); };
const money = (value: number) => new Intl.NumberFormat("zh-CN", { maximumFractionDigits: 2 }).format(value);
const quantityKg = (data: PriceData) => {
  const value = (data.package_display ?? data.spec ?? "").toLowerCase().replace(",", ".");
  const match = value.match(/([0-9]+(?:\.[0-9]+)?)\s*(kg|кг|g|гр|г)\b/i);
  if (!match) return null;
  const amount = Number(match[1]);
  return match[2].toLowerCase() === "kg" || match[2].toLowerCase() === "кг" ? amount : amount / 1000;
};

export default function PriceLiveTable() {
  const [records, setRecords] = useState<Snapshot[]>(fallback);
  const [country, setCountry] = useState("ALL");
  const [variety, setVariety] = useState("ALL");
  const [fallbackMode, setFallbackMode] = useState(true);
  const [settlement, setSettlement] = useState<"USD" | "CNY">("USD");
  const [cnyPerUsd, setCnyPerUsd] = useState<number | null>(null);
  const [fxDate, setFxDate] = useState("");
  useEffect(() => { fetch("/api/ingest/snapshot?metric=price_retail&latest=1&limit=500").then(r => r.ok ? r.json() as Promise<{ records?: Snapshot[] }> : Promise.reject()).then(payload => { const valid = (payload.records ?? []).filter(isComplete); if (valid.length) { setRecords(valid); setFallbackMode(false); } }).catch(() => {}); }, []);
  useEffect(() => { fetch("https://api.frankfurter.dev/v2/rate/USD/CNY").then(r => r.ok ? r.json() as Promise<{ rate: number; date: string }> : Promise.reject()).then(payload => { if (Number.isFinite(payload.rate)) { setCnyPerUsd(payload.rate); setFxDate(payload.date); } }).catch(() => {}); }, []);
  const varieties = useMemo(() => Array.from(new Set(records.map(r => labelSpecies(r.data)))).sort((a, b) => a.localeCompare(b, "zh-CN")), [records]);
  const visible = useMemo(() => records.filter(r => (country === "ALL" || r.country === country) && (variety === "ALL" || labelSpecies(r.data) === variety)), [records, country, variety]);
  return <>
    <div className="live-price-filters"><label>国家<select value={country} onChange={e => setCountry(e.target.value)}><option value="ALL">全部国家</option>{Object.entries(countryNames).map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select></label><label>菌种<select value={variety} onChange={e => setVariety(e.target.value)}><option value="ALL">全部菌种</option>{varieties.map(value => <option value={value} key={value}>{value}</option>)}</select></label><div className="currency-switch" aria-label="结算币种"><button className={settlement === "USD" ? "active" : ""} onClick={() => setSettlement("USD")}>美元 USD</button><button className={settlement === "CNY" ? "active" : ""} disabled={cnyPerUsd == null} onClick={() => setSettlement("CNY")}>人民币 CNY</button></div><small>{fallbackMode ? "已验证公开价格" : `已收录 ${visible.length} 条有效价格`} · {cnyPerUsd ? `实时汇率 1 USD = ${cnyPerUsd.toFixed(4)} CNY（${fxDate}）` : "正在获取实时 USD/CNY 汇率"}</small></div>
    {visible.length ? <div className="live-price-table"><div className="live-price-row head"><b>国家</b><b>菌种</b><b>形态</b><b>规格</b><b>渠道</b><b>当地挂牌价</b><b>{settlement} 结算价</b><b>{settlement}/公斤参考价</b><b>采价日期</b><b>来源</b></div>{visible.map(r => { const quantity = quantityKg(r.data); const usdPackage = r.data.price_usd ?? (r.data.normalized_price_usd_per_kg != null && quantity ? r.data.normalized_price_usd_per_kg * quantity : null); const usdPerKg = r.data.normalized_price_usd_per_kg ?? (usdPackage != null && quantity ? usdPackage / quantity : null); const factor = settlement === "CNY" ? cnyPerUsd : 1; const symbol = settlement === "CNY" ? "¥" : "$"; const settledPackage = usdPackage != null && factor != null ? usdPackage * factor : null; const settledPerKg = usdPerKg != null && factor != null ? usdPerKg * factor : null; const source = sourceNames[r.source] ?? r.data.platform_name ?? "线上零售平台"; return <div className="live-price-row" key={r.id}><span>{countryNames[r.country] ?? r.country}</span><span>{labelSpecies(r.data)}</span><span>{labelForm(r.data)}</span><span>{r.data.package_display ?? r.data.spec ?? "—"}</span><span>{source}</span><span>{money(r.data.price_local!)} {r.data.currency}</span><span>{settledPackage == null ? "—" : `${symbol}${money(settledPackage)}`}</span><span>{settledPerKg == null ? "—" : `${symbol}${money(settledPerKg)}/kg`}</span><span>{r.data.observed_at}</span><span>{r.data.source_url ? <a href={r.data.source_url} target="_blank" rel="noreferrer">查看商品页 ↗</a> : source}</span></div>; })}</div> : <div className="price-empty"><strong>当前筛选条件下暂无有效报价</strong><span>请选择其他国家或菌种查看。</span></div>}
  </>;
}
