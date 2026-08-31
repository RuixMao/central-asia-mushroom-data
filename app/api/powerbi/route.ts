import { desc, eq } from "drizzle-orm";
import { getDb } from "../../../db";
import { collectionErrors, collectionRuns, dailyPriceSummaries, platforms, priceObservations, products, species } from "../../../db/schema";
import scope from "../../../scope.json";

export const dynamic = "force-dynamic";

const csvCell = (value: unknown) => {
  const text = value == null ? "" : value instanceof Date ? value.toISOString() : typeof value === "object" ? JSON.stringify(value) : String(value);
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
};

const csv = (rows: Record<string, unknown>[]) => {
  if (!rows.length) return "";
  const headers = Object.keys(rows[0]);
  return `\uFEFF${headers.join(",")}\r\n${rows.map(row => headers.map(key => csvCell(row[key])).join(",")).join("\r\n")}`;
};

const countryNames: Record<string, string> = Object.fromEntries(scope.countries.map(country=>[country.code,country.name]));
const countryTiers: Record<string, number> = Object.fromEntries(scope.countries.map(country=>[country.code,country.tier]));
const speciesNames: Record<string, string> = Object.fromEntries(scope.species.map(species=>[species.slug,species.name]));
const customerText = (value: string | null) => value?.replace(/（老挝锚）|\(老挝锚\)/g, "").replace(/\s*\/\s*老挝邻国参考/g, "").replace(/供给锚/g, "市场参考").replace(/邻国锚/g, "周边市场价格").replace(/（待核）|\(待核\)/g, "") ?? value;

export async function GET(request: Request) {
  const params = new URL(request.url).searchParams;
  const table = params.get("table") ?? "prices";
  const format = params.get("format") ?? "json";
  const dateFrom = params.get("date_from");
  let records: Record<string, unknown>[];

  if (table === "prices") {
    const rows = await getDb().select({ price: priceObservations, product: products, platform: platforms }).from(priceObservations).innerJoin(products, eq(priceObservations.productId, products.id)).innerJoin(platforms, eq(products.platformId, platforms.id)).where(eq(priceObservations.status,"active")).orderBy(desc(priceObservations.observedAt)).limit(5000);
    records = rows.filter(row => !dateFrom || row.price.observationDate >= dateFrom).map(({ price, product, platform }) => ({
      observation_date: price.observationDate, observed_at: price.observedAt, product_id: product.id,
      country: product.country, country_name: countryNames[product.country] ?? product.country, city: customerText(product.city),
      species_id: product.speciesId, species_name: speciesNames[product.speciesId ?? ""] ?? product.speciesId,
      product_form: product.productForm, original_title: customerText(product.originalTitle), brand: product.brand,
      grade: typeof product.classificationEvidence?.grade === "string" ? product.classificationEvidence.grade : null,
      status: price.status, valid_until: price.validUntil, is_current: !price.validUntil || countryTiers[product.country]===3 || price.validUntil>=new Date().toISOString().slice(0,10),
      platform_id: platform.id, platform_name: customerText(platform.name), current_price: price.currentPrice,
      promotion_price: price.promotionPrice, currency: price.currency, normalized_quantity_kg: price.normalizedQuantityKg,
      package_value: price.packageValue, package_unit: price.packageUnit, raw_price_text: price.rawPriceText,
      source_url: price.sourceUrl, source_type: price.sourceType,
      normalized_price_per_kg: price.normalizedPricePerKg,
      normalized_usd_per_kg: price.normalizedPricePerKg && price.usdRateLocalPerUsd ? price.normalizedPricePerKg / price.usdRateLocalPerUsd : null,
      price_usd_per_package: price.priceUsd, usd_rate_local_per_usd: price.usdRateLocalPerUsd, fx_source: price.fxSource, fx_timestamp: price.fxTimestamp,
      in_stock: price.inStock, validation_status: price.validationStatus,
      sanity_outlier: price.sanityOutlier, sanity_reason: price.sanityReason,
    }));
  } else if (table === "daily") {
    const rows = await getDb().select().from(dailyPriceSummaries).orderBy(desc(dailyPriceSummaries.date)).limit(5000);
    records = rows.filter(row => !dateFrom || row.date >= dateFrom).map(row => ({ ...row, country_name: countryNames[row.country] ?? row.country, species_name: speciesNames[row.speciesId] ?? row.speciesId }));
  } else if (table === "runs") {
    records = (await getDb().select().from(collectionRuns).orderBy(desc(collectionRuns.startedAt)).limit(500)).map(row => ({ ...row, country_name: row.country ? countryNames[row.country] ?? row.country : "全部", duration_seconds: row.finishedAt ? (row.finishedAt.getTime() - row.startedAt.getTime()) / 1000 : null }));
  } else if (table === "errors") {
    records = await getDb().select().from(collectionErrors).orderBy(desc(collectionErrors.createdAt)).limit(2000);
  } else if (table === "products") {
    records = (await getDb().select().from(products).limit(5000)).map(row => ({ ...row, country_name: countryNames[row.country] ?? row.country, species_name: speciesNames[row.speciesId ?? ""] ?? row.speciesId }));
  } else if (table === "species") {
    records = await getDb().select().from(species);
  } else return Response.json({ error: "不支持的数据表" }, { status: 400 });

  if (format === "csv") return new Response(csv(records), { headers: { "content-type": "text/csv; charset=utf-8", "content-disposition": `inline; filename=${table}.csv`, "cache-control": "public, max-age=300" } });
  return Response.json({ records, count: records.length, generated_at: new Date().toISOString() },{headers:{"cache-control":"public, max-age=60, stale-while-revalidate=120"}});
}
