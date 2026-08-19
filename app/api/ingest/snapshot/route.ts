import { and, desc, eq } from "drizzle-orm";
import { getDb } from "../../../../db";
import { dataSnapshots } from "../../../../db/schema";

const metrics = new Set(["trade", "price", "price_retail", "logistics", "production", "source_health", "search_query_health", "macro", "market_avg_price", "fx", "freight", "port_status", "regulation", "event_calendar"]);
const countries = new Set(["KZ", "UZ", "KG", "TJ", "TM"]);
const authorized = (request: Request) => Boolean(process.env.CRON_SECRET) && request.headers.get("x-cron-secret") === process.env.CRON_SECRET;

export async function POST(request: Request) {
  if (!authorized(request)) return Response.json({ error: "Unauthorized" }, { status: 401 });
  const body = await request.json() as { metric?: string; country?: string; data?: Record<string, unknown>; source?: string };
  if (!metrics.has(body.metric ?? "") || !countries.has(body.country ?? "") || !body.data || !body.source) return Response.json({ error: "Invalid snapshot" }, { status: 400 });
  const id = crypto.randomUUID();
  const now = new Date();
  await getDb().insert(dataSnapshots).values({ id, metric: body.metric as "trade", country: body.country as "KZ", data: body.data, source: body.source, capturedAt: now, createdAt: now });
  return Response.json({ ok: true, id });
}

export async function GET(request: Request) {
  const params = new URL(request.url).searchParams;
  const metric = params.get("metric");
  const country = params.get("country");
  const limit = Math.min(Math.max(Number(params.get("limit") ?? (params.has("latest") ? 50 : 100)), 1), 10000);
  const filters = [];
  if (metric && metrics.has(metric)) filters.push(eq(dataSnapshots.metric, metric as "trade"));
  if (country && countries.has(country)) filters.push(eq(dataSnapshots.country, country as "KZ"));
  try {
    const candidates = await getDb().select().from(dataSnapshots).where(filters.length ? and(...filters) : undefined).orderBy(desc(dataSnapshots.capturedAt)).limit(limit);
    const fields=["hs","year","month","partner_code","status","period","period_type","date","route","currency","source_id","rule_type","port"];
    const rows=candidates.filter(row=>fields.every(field=>!params.has(field)||String((row.data as Record<string,unknown>)[field]??"")===params.get(field)));
    return Response.json({ records: rows, count: rows.length });
  } catch {
    return Response.json({ records: [], count: 0, fallback: true });
  }
}
