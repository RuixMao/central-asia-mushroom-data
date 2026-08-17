"use client";

import { useEffect, useMemo, useState } from "react";
import { countryOptions, mirrorRecords } from "../data";

type MirrorItem = {
  countryCode: string;
  country: string;
  hs: string;
  product: string;
  importerCifUsd: number | null;
  chinaFobUsd: number | null;
  officialQuantityKg?: number;
  confirmedTradeUsd?: number;
  confirmedQuantityKg?: number;
  confirmedPartners?: string[];
  confidence: "A+" | "A" | "B+" | "B";
  confidenceBasis: string;
};

const productNames: Record<string, string> = {
  "070951": "鲜或冷藏蘑菇",
  "070959": "其他鲜或冷藏蘑菇",
  "200310": "加工保藏蘑菇",
};
const fallback: MirrorItem[] = mirrorRecords;
const money = (value: number | null | undefined) => value == null ? "—" : `$${value.toLocaleString("en-US")}`;
const gapRate = (importer: number | null, exporter: number | null) => importer === null || exporter === null ? null : Math.abs(importer - exporter) / Math.max(importer, exporter) * 100;

export default function MirrorLiveGrid() {
  const [records, setRecords] = useState<MirrorItem[]>(fallback);

  useEffect(() => {
    fetch("/api/trade?mode=mirror&year=2024")
      .then((response) => response.ok ? response.json() as Promise<{ records?: MirrorItem[] }> : Promise.reject())
      .then((payload) => {
        if (!payload.records?.length) return;
        setRecords(fallback.map((base) => ({
          ...payload.records!.find((item) => item.countryCode === base.countryCode && item.hs === base.hs),
          ...base,
        })));
      })
      .catch(() => {});
  }, []);

  const countries = useMemo(() => countryOptions.filter((country) => country.code !== "ALL"), []);

  return <div className="mirror-country-list">{countries.map((country) => {
    const items = records.filter((record) => record.countryCode === country.code && (record.importerCifUsd !== null || record.chinaFobUsd !== null || record.confirmedTradeUsd));
    return <section className="mirror-country" key={country.code}>
      <header><div><b>{country.label}</b><span>{country.code}</span></div><small>{items.length ? `${items.length} 个重点品类` : "本期暂无公开数据"}</small></header>
      {items.length ? <div className="mirror-grid">{items.map((record) => {
        const gap = gapRate(record.importerCifUsd, record.chinaFobUsd);
        const hasOfficial = record.importerCifUsd !== null;
        const status = hasOfficial ? `2024 年进口申报，${record.officialQuantityKg?.toLocaleString("en-US")} 公斤` : `已覆盖${record.confirmedPartners?.join("、")}`;
        return <article key={`${record.countryCode}-${record.hs}`}>
          <span className="mirror-grade" title={record.confidenceBasis}>{record.confidence}</span>
          <span className="mirror-category">{productNames[record.hs] ?? record.product}</span>
          <h3>HS {record.hs}</h3>
          <div><p>{hasOfficial ? "当地公布进口额" : "已确认贸易额"}<b>{money(hasOfficial ? record.importerCifUsd : record.confirmedTradeUsd)}</b></p><p>{hasOfficial ? "其中来自中国" : "中国对当地出口额"}<b>{money(record.chinaFobUsd)}</b></p></div>
          {hasOfficial ? <strong>{gap === null ? "—" : `${gap.toFixed(1)}%`}<small>两地统计差异</small></strong> : <strong>{record.confirmedQuantityKg?.toLocaleString("en-US") ?? "—"}<small>已确认数量（公斤）</small></strong>}
          <i>{status}</i><small className="mirror-basis">{record.confidenceBasis}</small>
        </article>;
      })}</div> : <div className="mirror-empty"><b>本期暂无可展示数据</b><p>相关市场信息将在取得可靠公开资料后更新。</p></div>}
    </section>;
  })}</div>;
}
