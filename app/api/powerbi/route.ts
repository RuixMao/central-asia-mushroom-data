import { and, desc, eq } from "drizzle-orm";
import { getDb } from "../../../db";
import { collectionErrors, collectionRuns, dailyPriceSummaries, platforms, priceObservations, products, species } from "../../../db/schema";
import { env } from "cloudflare:workers";
import { ensureSeaPriceSeed } from "../../sea-price-seed";
import { ensureLaosRawPriceIntel } from "../../laos-raw-price-intel";
import { ensureFiveCountryPriceSeed } from "../../five-country-price-seed";

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

const countryNames: Record<string, string> = { KZ: "哈萨克斯坦", UZ: "乌兹别克斯坦", KG: "吉尔吉斯斯坦", TJ: "塔吉克斯坦", TM: "土库曼斯坦", LA: "老挝", VN: "越南", TH: "泰国", MM: "缅甸", KH: "柬埔寨" };
const speciesNames: Record<string, string> = { button_mushroom: "双孢菇", oyster_mushroom: "平菇", shiitake: "香菇", enoki: "金针菇", king_oyster_mushroom: "杏鲍菇", honey_fungus: "蜜环菌", suillus: "乳牛肝菌", porcini: "牛肝菌", shimeji: "真姬菇", wood_ear: "木耳", snow_fungus: "银耳", morel: "羊肚菌", chanterelle: "鸡油菌" };

export async function GET(request: Request) {
  await ensureSeaPriceSeed((env as unknown as {DB:D1Database}).DB);
  await ensureLaosRawPriceIntel((env as unknown as {DB:D1Database}).DB);
  await ensureFiveCountryPriceSeed((env as unknown as {DB:D1Database}).DB);
  const params = new URL(request.url).searchParams;
  const table = params.get("table") ?? "prices";
  const format = params.get("format") ?? "json";
  const dateFrom = params.get("date_from");
  let records: Record<string, unknown>[];

  if (table === "prices") {
    const filters = [eq(priceObservations.validationStatus, "valid")];
    const rows = await getDb().select({ price: priceObservations, product: products, platform: platforms }).from(priceObservations).innerJoin(products, eq(priceObservations.productId, products.id)).innerJoin(platforms, eq(products.platformId, platforms.id)).where(and(...filters)).orderBy(desc(priceObservations.observedAt)).limit(5000);
    records = rows.filter(row => !dateFrom || row.price.observationDate >= dateFrom).map(({ price, product, platform }) => ({
      observation_date: price.observationDate, observed_at: price.observedAt, product_id: product.id,
      country: product.country, country_name: countryNames[product.country] ?? product.country, city: product.city,
      species_id: product.speciesId, species_name: speciesNames[product.speciesId ?? ""] ?? product.speciesId,
      product_form: product.productForm, original_title: product.originalTitle, brand: product.brand,
      platform_id: platform.id, platform_name: platform.name, current_price: price.currentPrice,
      promotion_price: price.promotionPrice, currency: price.currency, normalized_quantity_kg: price.normalizedQuantityKg,
      package_value: price.packageValue, package_unit: price.packageUnit, raw_price_text: price.rawPriceText,
      normalized_price_per_kg: price.normalizedPricePerKg,
      normalized_usd_per_kg: price.normalizedPricePerKg && price.usdRateLocalPerUsd ? price.normalizedPricePerKg / price.usdRateLocalPerUsd : null,
      price_usd_per_package: price.priceUsd, in_stock: price.inStock, validation_status: price.validationStatus,
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
  return Response.json({ records, count: records.length, generated_at: new Date().toISOString() },{headers:{"cache-control":"public, max-age=60, stale-while-revalidate=600"}});
}
