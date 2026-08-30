"use client";

import { useEffect, useMemo, useState } from "react";

type PriceRecord = {
  price: {
    observationDate: string;
    currentPrice: number | null;
    regularPrice: number | null;
    promotionPrice: number | null;
    currency: string;
    packageValue: number | null;
    packageUnit: string | null;
    normalizedPricePerKg: number | null;
    priceUsd: number | null;
    inStock: boolean | null;
    observedAt: string | number;
    validationStatus: string;
    sanityOutlier?: boolean;
    sanityReason?: string | null;
    sourceUrl: string;
  };
  product: {
    id: string;
    country: string;
    city: string;
    originalTitle: string;
    speciesId: string | null;
    productForm: string;
    classificationConfidence: number;
    classificationStatus: string;
  };
  platform: { id: string; name: string };
};

const PAGE_SIZE = 20;
const countryNames: Record<string, string> = { KZ: "哈萨克斯坦", UZ: "乌兹别克斯坦", KG: "吉尔吉斯斯坦", TJ: "塔吉克斯坦", TM: "土库曼斯坦", LA: "老挝", VN: "越南", TH: "泰国", MM: "缅甸", KH: "柬埔寨" };
const speciesNames: Record<string, string> = {
  agaricus_bisporus: "双孢菇", pleurotus_ostreatus: "平菇", flammulina_velutipes: "金针菇", lentinula_edodes: "香菇",
  pleurotus_eryngii: "杏鲍菇", button_mushroom: "双孢菇", oyster_mushroom: "平菇", enoki: "金针菇", shiitake: "香菇",
  king_oyster_mushroom: "杏鲍菇", wood_ear: "木耳", mixed_species: "混合菌菇", unknown_species: "未识别", suillus: "牛肝菌属",
};
const formNames: Record<string, string> = { fresh: "鲜品", chilled: "冷藏", frozen: "冷冻", dried: "干制", pickled: "腌制", canned: "罐藏", powder: "菌粉", mixed: "混合", unknown: "未知" };
const fmt = (n: number | null, d = 2) => n == null ? "—" : n.toLocaleString("zh-CN", { maximumFractionDigits: d });
const currentPrice = (r: PriceRecord) => r.price.promotionPrice ?? r.price.currentPrice;
const usdPerKg = (r: PriceRecord) => {
  const local = currentPrice(r);
  if (!local || !r.price.priceUsd || !r.price.normalizedPricePerKg) return null;
  return r.price.normalizedPricePerKg * r.price.priceUsd / local;
};
const suspiciousTitle = (title: string) => /PVC|поливинил|габарит|дача|сад|огород|семен|мицел|книги|гавриш/i.test(title);
const reviewReason = (r: PriceRecord) => {
  const usdKg = usdPerKg(r);
  if (r.price.sanityOutlier) return r.price.sanityReason ?? "超出合理价格区间";
  if (suspiciousTitle(r.product.originalTitle)) return "疑似非食品商品";
  if (r.product.classificationStatus !== "classified" || r.product.classificationConfidence < .8) return "分类待复核";
  if (r.price.validationStatus !== "valid") return "价格校验未通过";
  if (!r.price.packageValue || !r.price.packageUnit || !r.price.normalizedPricePerKg || !usdKg) return "重量规格缺失";
  if (r.price.inStock === false) return "商品缺货";
  if (r.product.productForm === "fresh" && (usdKg < .25 || usdKg > 30)) return "鲜品价格异常";
  return null;
};
const median = (values: number[]) => values.length ? [...values].sort((a, b) => a - b)[Math.floor(values.length / 2)] : null;

export default function MarketPanel({ onState }: { onState: (state: "loading" | "live" | "fallback") => void }) {
  const [records, setRecords] = useState<PriceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [country, setCountry] = useState("ALL");
  const [city, setCity] = useState("ALL");
  const [species, setSpecies] = useState("ALL");
  const [form, setForm] = useState("ALL");
  const [platform, setPlatform] = useState("ALL");
  const [date, setDate] = useState("");
  const [quality, setQuality] = useState("valid");
  const [page, setPage] = useState(1);

  useEffect(() => {
    let active = true;
    const load = () => fetch(`/api/prices?ts=${Date.now()}`, { cache: "no-store" })
      .then(r => r.json())
      .then((p: { records?: PriceRecord[] }) => {
        if (!active) return;
        const incoming = p.records ?? [];
        setRecords(incoming);
        setDate(previous => previous || [...new Set(incoming.map(r => r.price.observationDate))].sort().at(-1) || "");
        onState(incoming.length ? "live" : "fallback");
      })
      .catch(() => onState("fallback"))
      .finally(() => setLoading(false));
    load();
    const timer = setInterval(load, 30000);
    return () => { active = false; clearInterval(timer); };
  }, [onState]);

  const uniqueRecords = useMemo(() => {
    const seen = new Set<string>();
    return records.filter(r => {
      const key = `${r.price.observationDate}|${r.platform.id}|${r.price.sourceUrl}|${r.product.originalTitle}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }, [records]);
  const dates = useMemo(() => [...new Set(uniqueRecords.map(r => r.price.observationDate))].sort().reverse(), [uniqueRecords]);
  const matchDimensions = (r: PriceRecord) => (country === "ALL" || r.product.country === country) && (city === "ALL" || r.product.city === city) && (species === "ALL" || r.product.speciesId === species) && (form === "ALL" || r.product.productForm === form) && (platform === "ALL" || r.platform.id === platform);
  const dimensionRows = useMemo(() => uniqueRecords.filter(matchDimensions), [uniqueRecords, country, city, species, form, platform]);
  const filtered = useMemo(() => dimensionRows.filter(r => (!date || r.price.observationDate === date) && (quality === "all" || (quality === "valid" ? !reviewReason(r) : !!reviewReason(r)))), [dimensionRows, date, quality]);
  const validRows = filtered.filter(r => !reviewReason(r));
  const usdValues = validRows.map(usdPerKg).filter((x): x is number => x != null).sort((a, b) => a - b);
  const reviewCount = dimensionRows.filter(r => (!date || r.price.observationDate === date) && !!reviewReason(r)).length;
  const dayRows = dimensionRows.filter(r => !date || r.price.observationDate === date);
  const validRate = dayRows.length ? (dayRows.length - reviewCount) / dayRows.length : null;
  const grade = validRate == null ? "—" : validRate >= .9 ? "A" : validRate >= .75 ? "B" : validRate >= .55 ? "C" : "D";
  const latest = filtered.length ? Math.max(...filtered.map(r => new Date(r.price.observedAt).getTime())) : null;
  const options = (key: "city" | "species" | "form" | "platform") => [...new Set(uniqueRecords.map(r => key === "city" ? r.product.city : key === "species" ? r.product.speciesId ?? "unknown_species" : key === "form" ? r.product.productForm : r.platform.id))];
  const byPlatform = [...new Set(validRows.map(r => r.platform.id))].map(id => {
    const rows = validRows.filter(r => r.platform.id === id);
    const value = median(rows.map(usdPerKg).filter((x): x is number => x != null));
    return { id, name: rows[0].platform.name, value };
  }).filter(x => x.value != null).sort((a, b) => a.value! - b.value!);
  const maxPlatform = Math.max(1, ...byPlatform.map(x => x.value!));
  const trend = dates.slice(0, 7).reverse().map(day => {
    const values = dimensionRows.filter(r => r.price.observationDate === day && !reviewReason(r)).map(usdPerKg).filter((x): x is number => x != null);
    return { day, value: median(values), count: values.length };
  });
  const trendMax = Math.max(1, ...trend.map(x => x.value ?? 0));
  const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const visibleRows = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  useEffect(() => setPage(1), [country, city, species, form, platform, date, quality]);

  const reset = () => { setCountry("ALL"); setCity("ALL"); setSpecies("ALL"); setForm("ALL"); setPlatform("ALL"); setDate(dates[0] ?? ""); setQuality("valid"); };
  const exportCsv = () => {
    const header = ["日期", "国家", "城市", "菌种", "形态", "平台", "商品", "规格", "原币价格", "币种", "USD/kg", "状态", "复核原因", "来源"];
    const rows = filtered.map(r => [r.price.observationDate, countryNames[r.product.country] ?? r.product.country, r.product.city, speciesNames[r.product.speciesId ?? "unknown_species"] ?? r.product.speciesId, formNames[r.product.productForm] ?? r.product.productForm, r.platform.name, r.product.originalTitle, `${r.price.packageValue ?? ""} ${r.price.packageUnit ?? ""}`.trim(), currentPrice(r) ?? "", r.price.currency, usdPerKg(r)?.toFixed(2) ?? "", reviewReason(r) ? "待复核" : "有效", reviewReason(r) ?? "", r.price.sourceUrl]);
    const csv = [header, ...rows].map(row => row.map(cell => `"${String(cell ?? "").replaceAll('"', '""')}"`).join(",")).join("\n");
    const link = document.createElement("a");
    link.href = URL.createObjectURL(new Blob(["\ufeff" + csv], { type: "text/csv;charset=utf-8" }));
    link.download = `菌业出海价格_${date || "全部日期"}.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  return <>
    <section className="intel-hero terminal-controls"><div><span>完整价格依据</span><h1>按国家、品类和规格核对当地价格</h1><p>先筛选您的目标市场和产品，再比较可用报价。跨国比较统一换算为美元每公斤，同时保留原币、包装规格、日期和来源；未通过检查的记录不会计入结果。</p></div><div className="asset-summary"><strong>{loading ? "—" : validRows.length || "—"}</strong><span>当前可比较报价</span><strong>{loading ? "—" : new Set(validRows.map(r => r.platform.id)).size || "—"}</strong><span>当前覆盖渠道</span></div></section>
    <section className="coverage-gap-strip"><b>最新采集覆盖</b>{Object.entries(countryNames).map(([code, name]) => { const rows = uniqueRecords.filter(r => r.product.country === code && r.price.observationDate === dates[0]); const valid = rows.filter(r => !reviewReason(r)).length; return <span className={valid ? "covered" : "gap"} key={code}>{name}：{valid ? `${valid} 条有效报价` : "今日暂无有效报价"}</span>; })}</section>
    <section className="live-price-filters terminal-price-filters">
      <label>国家<select value={country} onChange={e => { setCountry(e.target.value); setCity("ALL"); }}><option value="ALL">全部国家</option>{Object.entries(countryNames).map(([v, l]) => <option value={v} key={v}>{l}</option>)}</select></label>
      <label>城市<select value={city} onChange={e => setCity(e.target.value)}><option value="ALL">全部城市</option>{options("city").map(v => <option key={v}>{v}</option>)}</select></label>
      <label>菌种<select value={species} onChange={e => setSpecies(e.target.value)}><option value="ALL">全部菌种</option>{options("species").map(v => <option value={v} key={v}>{speciesNames[v] ?? v}</option>)}</select></label>
      <label>形态<select value={form} onChange={e => setForm(e.target.value)}><option value="ALL">全部形态</option>{options("form").map(v => <option value={v} key={v}>{formNames[v] ?? v}</option>)}</select></label>
      <label>平台<select value={platform} onChange={e => setPlatform(e.target.value)}><option value="ALL">全部平台</option>{options("platform").map(v => <option value={v} key={v}>{uniqueRecords.find(r => r.platform.id === v)?.platform.name ?? v}</option>)}</select></label>
      <label>采集日期<select value={date} onChange={e => setDate(e.target.value)}><option value="">全部历史</option>{dates.map(v => <option value={v} key={v}>{v}{v === dates[0] ? "（最新）" : ""}</option>)}</select></label>
      <label>数据状态<select value={quality} onChange={e => setQuality(e.target.value)}><option value="valid">仅有效报价</option><option value="review">仅待复核</option><option value="all">全部记录</option></select></label>
      <button type="button" className="terminal-reset" onClick={reset}>清空筛选</button>
    </section>
    <section className="intel-kpis"><article><span>最低有效价</span><strong>{usdValues.length ? `$${fmt(usdValues[0])}/kg` : "—"}</strong><small>统一美元每公斤口径</small></article><article><span>中位有效价</span><strong>{usdValues.length ? `$${fmt(median(usdValues))}/kg` : "—"}</strong><small>仅纳入可比重量规格</small></article><article><span>最高有效价</span><strong>{usdValues.length ? `$${fmt(usdValues.at(-1)!)} /kg` : "—"}</strong><small>鲜品异常值自动转待复核</small></article><article><span>待复核 / 质量</span><strong>{reviewCount} · {grade}</strong><small>有效率 {validRate == null ? "—" : `${(validRate * 100).toFixed(0)}%`}，A ≥ 90%</small></article></section>
    <section className="terminal-trend-panel"><div className="intel-panel-head"><div><span>7-DAY VERIFIED TREND</span><h2>近七次采集 · 有效价中位数</h2></div><small>USD/kg · 当前国家/菌种/形态/平台筛选</small></div><div className="terminal-trend-chart">{trend.map(point => <div className="trend-column" key={point.day}><strong>{point.value == null ? "—" : `$${fmt(point.value)}`}</strong><i><em style={{ height: `${point.value == null ? 0 : Math.max(8, point.value / trendMax * 100)}%` }} /></i><span>{point.day.slice(5)}</span><small>{point.count} 条</small></div>)}</div></section>
    <section className="terminal-insights"><article><span>平台有效价对比 · USD/kg</span>{byPlatform.length ? byPlatform.map(x => <div className="platform-price-bar" key={x.id}><b>{x.name}</b><i style={{ width: `${x.value! / maxPlatform * 100}%` }} /><strong>${fmt(x.value)}/kg</strong></div>) : <p>当前筛选条件下暂无可比较的有效报价。</p>}</article><article><span>数据质量</span><dl><div><dt>口径</dt><dd>USD/kg</dd></div><div><dt>去重后记录</dt><dd>{dayRows.length}</dd></div><div><dt>最近采集</dt><dd>{latest ? new Date(latest).toLocaleString("zh-CN") : "—"}</dd></div><div><dt>质量等级</dt><dd>{grade}</dd></div></dl><p className="quality-note">评级依据：有效记录占当前筛选记录的比例；疑似非食品、规格缺失、分类未通过及异常鲜品价格均转入待复核。</p></article></section>
    <section className="terminal-product-entry"><div><span>看完价格以后</span><h2>下一步是判断价格能否转化为利润空间</h2><p>公开挂牌价只是起点，还应结合采购量、运输、损耗、税费和真实成交条件验证。</p></div><div className="terminal-product-cards"><a href="/reports/daily"><b>查看今天有哪些变化</b><small>阅读最新行情和风险提示</small></a><a href="/pricing"><b>持续跟踪我的目标市场</b><small>选择国家、品类与更新频率</small></a><a href="/expand/contact"><b>核算我的产品是否值得进入</b><small>提交产品、成本和目标市场</small></a></div></section>
    <section className="intel-table-panel"><div className="intel-panel-head"><div><span>TRACEABLE SKU OBSERVATIONS</span><h2>每日 SKU 明细</h2></div><div className="terminal-table-actions"><small>页面观察价 · 非成交价 · 共 {filtered.length} 条</small><button type="button" onClick={exportCsv} disabled={!filtered.length}>导出当前结果 CSV</button></div></div><div className="intel-table"><div className="intel-row sku-price-row head"><span>日期 / 市场</span><span>商品 / 分类</span><span>平台 / 规格</span><span>原币 / USD/kg</span><span>状态 / 依据</span><span>来源</span></div>{visibleRows.map(r => { const reason = reviewReason(r); return <div className="intel-row sku-price-row" key={`${r.product.id}-${r.price.observationDate}-${r.price.sourceUrl}`}><span><b>{r.price.observationDate}</b><small>{countryNames[r.product.country]} · {r.product.city}</small></span><span><b>{r.product.originalTitle}</b><small>{speciesNames[r.product.speciesId ?? "unknown_species"] ?? r.product.speciesId} · {formNames[r.product.productForm] ?? r.product.productForm} · {(r.product.classificationConfidence * 100).toFixed(0)}%</small></span><span><b>{r.platform.name}</b><small>{r.price.packageValue ?? "—"} {r.price.packageUnit ?? ""}</small></span><span><b>{fmt(currentPrice(r))} {r.price.currency}</b><small>{usdPerKg(r) == null ? "USD/kg 待复核" : `$${fmt(usdPerKg(r))}/kg`}</small></span><span><b className={reason ? "status-review" : "status-valid"}>{reason ? "待复核" : "有效"}</b><small>{reason ?? "已通过规格与价格校验"}</small></span><span><a href={r.price.sourceUrl} target="_blank" rel="noreferrer">商品页 ↗</a></span></div>; })}{!loading && !filtered.length && <div className="daily-empty"><strong>暂无符合条件的价格记录</strong><p>可切换数据状态或清空筛选；缺失数据不会用零值代替。</p></div>}{loading && <div className="daily-empty"><strong>正在读取正式价格库…</strong></div>}</div>{filtered.length > PAGE_SIZE && <div className="terminal-pagination"><button disabled={page === 1} onClick={() => setPage(p => p - 1)}>上一页</button><span>第 {page} / {pages} 页</span><button disabled={page === pages} onClick={() => setPage(p => p + 1)}>下一页</button></div>}</section>
  </>;
}
