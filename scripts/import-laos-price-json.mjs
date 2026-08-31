import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join } from "node:path";

const input = process.argv[2];
if (!input) throw new Error("JSON path required");
const rows = JSON.parse(readFileSync(input, "utf8"));
const q = value => value == null ? "NULL" : `'${String(value).replaceAll("'", "''")}'`;
const n = value => value == null || value === "" ? "NULL" : String(Number(value));
const hash = value => createHash("sha256").update(value).digest("hex").slice(0, 18);
const firstNumber = value => {
  const match = String(value ?? "").match(/\d+(?:\.\d+)?/);
  return match ? Number(match[0]) : null;
};
const priceParts = value => {
  const matches = String(value ?? "").match(/\d+(?:\.\d+)?/g)?.map(Number) ?? [];
  return { low: matches[0] ?? null, high: matches[1] ?? null };
};
const observedAt = Date.now();
const results = [];
const wrangler = join(process.cwd(), "node_modules", "wrangler", "bin", "wrangler.js");

for (const [index, row] of rows.entries()) {
  const local = priceParts(row.price_local);
  const usd = priceParts(row.usd_per_kg);
  const effective = local.low == null && row.currency === "USD" ? usd : local;
  const key = [row.country, row.species, row.platform, row.data_date, row.price_local, row.usd_per_kg, row.source_url].join("|");
  const id = hash(key);
  const platformId = `json_la_${hash(row.platform)}`;
  const pointId = `json_la_point_${hash(`${row.platform}|${row.city}`)}`;
  const sku = `json_la_${id}`;
  const productId = `${platformId}:${pointId}:${sku}`;
  const evidence = JSON.stringify({
    country: row.country, country_name: row.country_name, city: row.city,
    species: row.species, species_cn: row.species_cn, product_name: row.product_name,
    form: row.form, spec: row.spec, price_local: row.price_local, currency: row.currency,
    usd_per_kg: row.usd_per_kg, platform: row.platform, source_url: row.source_url,
    data_date: row.data_date, grade: row.grade, price_type: row.price_type,
    notes: row.notes, import_policy: "v5_raw_price_pool"
  });
  const rawPrice = row.price_local
    ? `${row.price_local} ${row.currency}`
    : `${row.usd_per_kg} USD/kg`;
  const confidence = row.grade === "A" ? 0.95 : row.grade === "B" ? 0.8 : row.grade === "C" ? 0.6 : 0.4;
  const sql = `
INSERT INTO species(id,name_zh,name_en,dictionary_version,review_status)
VALUES(${q(row.species)},${q(row.species_cn)},${q(row.species)},'json-v1','raw')
ON CONFLICT(id) DO UPDATE SET name_zh=excluded.name_zh;
INSERT INTO platforms(id,name,country,collection_method,status,updated_at)
VALUES(${q(platformId)},${q(row.platform)},'LA','json_raw_price_pool','active',${observedAt})
ON CONFLICT(id) DO UPDATE SET name=excluded.name,status='active',updated_at=excluded.updated_at;
INSERT INTO collection_points(id,country,city,platform_id,timezone,active,public_label)
VALUES(${q(pointId)},'LA',${q(row.city)},${q(platformId)},'Asia/Vientiane',1,${q(row.city)})
ON CONFLICT(id) DO UPDATE SET active=1,public_label=excluded.public_label;
INSERT INTO products(id,platform_id,platform_product_id,collection_point_id,country,city,product_url,original_title,original_description,original_category,original_language,species_id,product_form,classification_status,classification_confidence,classification_evidence,first_seen_at,last_seen_at,active)
VALUES(${q(productId)},${q(platformId)},${q(sku)},${q(pointId)},'LA',${q(row.city)},${q(row.source_url)},${q(row.product_name)},${q(row.notes)},${q(row.species_cn)},'原文',${q(row.species)},${q(row.form)},'classified',${confidence},${q(evidence)},${observedAt},${observedAt},1)
ON CONFLICT(platform_id,collection_point_id,platform_product_id) DO UPDATE SET product_url=excluded.product_url,original_title=excluded.original_title,original_description=excluded.original_description,original_category=excluded.original_category,product_form=excluded.product_form,classification_evidence=excluded.classification_evidence,last_seen_at=excluded.last_seen_at,active=1;
INSERT OR IGNORE INTO price_observations(id,product_id,observed_at,observation_date,current_price,regular_price,currency,package_unit,normalized_price_per_kg,usd_rate_local_per_usd,fx_source,in_stock,raw_price_text,source_url,source_type,collection_status,validation_status,validation_errors,sanity_outlier,sanity_reason,created_at)
SELECT ${q(`${sku}:${row.data_date}`)},${q(productId)},${observedAt},${q(row.data_date)},${n(effective.low)},${n(effective.high)},${q(row.currency)},${q(row.spec)},${n(usd.low)},${usd.low == null ? "NULL" : "1"},${q("JSON 原值；未换算")},1,${q(rawPrice)},${q(row.source_url)},'json_raw_price_pool','collected','valid',${q(evidence)},0,${q(row.notes)},${observedAt}
WHERE NOT EXISTS (
  SELECT 1 FROM price_observations po
  JOIN products p ON p.id=po.product_id
  JOIN platforms pf ON pf.id=p.platform_id
  WHERE p.country='LA' AND p.species_id=${q(row.species)} AND pf.name=${q(row.platform)}
    AND po.observation_date=${q(row.data_date)} AND po.raw_price_text=${q(rawPrice)}
);`;
  const run = spawnSync(process.execPath, [wrangler, "d1", "execute", "yinheng-market-data", "--remote", "--config", "wrangler.production.jsonc", "--command", sql], { encoding: "utf8", cwd: process.cwd() });
  results.push({ index: index + 1, product: row.product_name, ok: run.status === 0, output: `${run.stdout ?? ""}${run.stderr ?? ""}${run.error ?? ""}`.slice(-1000) });
  if (run.status !== 0) {
    const retry = spawnSync(process.execPath, [wrangler, "d1", "execute", "yinheng-market-data", "--remote", "--config", "wrangler.production.jsonc", "--command", sql], { encoding: "utf8", cwd: process.cwd() });
    results[results.length - 1] = { index: index + 1, product: row.product_name, ok: retry.status === 0, retried: true, output: `${retry.stdout ?? ""}${retry.stderr ?? ""}${retry.error ?? ""}`.slice(-1000) };
  }
}
console.log(JSON.stringify({ input_count: rows.length, success: results.filter(x => x.ok).length, failed: results.filter(x => !x.ok), results }, null, 2));
