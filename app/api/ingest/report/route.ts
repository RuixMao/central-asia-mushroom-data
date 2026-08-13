import { and, desc, eq } from "drizzle-orm";
import { getDb } from "../../../../db";
import { reportSources, reports } from "../../../../db/schema";

const countries = new Set(["KZ", "UZ", "KG", "TJ", "TM"]);
const types = new Set(["daily", "weekly", "monthly"]);
const authorized = (request: Request) => Boolean(process.env.CRON_SECRET) && request.headers.get("x-cron-secret") === process.env.CRON_SECRET;
const slugify = (title: string) => `${new Date().toISOString().slice(0,10)}-${title.toLowerCase().replace(/[^a-z0-9\u4e00-\u9fff]+/g,"-").replace(/^-|-$/g,"").slice(0,48)}-${crypto.randomUUID().slice(0,6)}`;
type Source={evidence_id?:string;document_id?:string;source_type?:string;title?:string;url?:string;publisher?:string;published_at?:string;retrieved_at?:string};

export async function POST(request: Request) {
  if (!authorized(request)) return Response.json({ error: "Unauthorized" }, { status: 401 });
  const body = await request.json() as { title?: string; type?: string; summary?: string; body?: string; country?: string; aiGenerated?: boolean; sources?:Source[] };
  if (!body.title || !body.summary || !body.body || !types.has(body.type ?? "") || !countries.has(body.country ?? "")) return Response.json({ error: "Invalid report" }, { status: 400 });
  const id = crypto.randomUUID(), slug = slugify(body.title), now = new Date();
  await getDb().insert(reports).values({ id, slug, title: body.title, type: body.type as "daily", summary: body.summary, body: body.body, country: body.country as "KZ", aiGenerated: body.aiGenerated !== false, publishedAt: now, createdAt: now });
  if(body.sources?.length){
    const sourceRows=body.sources.flatMap(source=>{
      const publishedAt=new Date(source.published_at??""),retrievedAt=new Date(source.retrieved_at??"");
      if(!source.evidence_id||!source.source_type||!source.title||!source.url||!source.publisher||Number.isNaN(publishedAt.getTime())||Number.isNaN(retrievedAt.getTime()))return [];
      return [{id:crypto.randomUUID(),reportId:id,evidenceId:source.evidence_id,documentId:source.document_id||null,sourceType:source.source_type,title:source.title,url:source.url,publisher:source.publisher,publishedAt,retrievedAt}];
    });
    if(sourceRows.length)await getDb().insert(reportSources).values(sourceRows);
  }
  return Response.json({ ok: true, slug });
}

export async function GET(request: Request) {
  const params = new URL(request.url).searchParams, filters = [];
  const type = params.get("type"), country = params.get("country"), slug = params.get("slug");
  if (type && types.has(type)) filters.push(eq(reports.type, type as "daily"));
  if (country && countries.has(country)) filters.push(eq(reports.country, country as "KZ"));
  if (slug) filters.push(eq(reports.slug, slug));
  try {
    const rows = await getDb().select().from(reports).where(filters.length ? and(...filters) : undefined).orderBy(desc(reports.publishedAt)).limit(slug ? 1 : 100);
    const sources=slug&&rows[0]?await getDb().select().from(reportSources).where(eq(reportSources.reportId,rows[0].id)).orderBy(reportSources.evidenceId):[];
    return Response.json({ records: rows, count: rows.length, sources });
  } catch { return Response.json({ records: [], count: 0, fallback: true }); }
}
