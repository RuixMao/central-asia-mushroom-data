import { and, desc, eq } from "drizzle-orm";
import { env } from "cloudflare:workers";
import { getDb } from "../../../../db";
import { reportSources, reports } from "../../../../db/schema";

const countries = new Set(["KZ", "UZ", "KG", "TJ", "TM", "LA", "VN", "TH", "MM", "KH"]);
const types = new Set(["daily", "weekly", "monthly", "quarterly", "annual"]);
const supersededSlugs = new Set(["2026-08-13-中亚菌类市场研究日报-2026-08-13-dc3459"]);
const authorized = (request: Request) => Boolean(process.env.CRON_SECRET) && request.headers.get("x-cron-secret") === process.env.CRON_SECRET;
const slugify = (title: string) => `${new Date().toISOString().slice(0,10)}-${title.toLowerCase().replace(/[^a-z0-9\u4e00-\u9fff]+/g,"-").replace(/^-|-$/g,"").slice(0,48)}-${crypto.randomUUID().slice(0,6)}`;
type Source={evidence_id?:string;document_id?:string;source_type?:string;title?:string;url?:string;publisher?:string;published_at?:string;retrieved_at?:string};

export async function POST(request: Request) {
  if (!authorized(request)) return Response.json({ error: "Unauthorized" }, { status: 401 });
  const body = await request.json() as { title?: string; type?: string; summary?: string; body?: string; country?: string; aiGenerated?: boolean; sources?:Source[] };
  if (!body.title || !body.summary || !body.body || !types.has(body.type ?? "") || !countries.has(body.country ?? "")) return Response.json({ error: "Invalid report" }, { status: 400 });
  const id = crypto.randomUUID(), slug = slugify(body.title), now = new Date();
  const seen=new Set<string>(),sources=[];
  for(const source of body.sources??[]){
    const publishedAt=Date.parse(source.published_at??""),retrievedAt=Date.parse(source.retrieved_at??"");
    if(!source.evidence_id||seen.has(source.evidence_id)||!source.source_type||!source.title||!source.url||!source.publisher||!Number.isFinite(publishedAt)||!Number.isFinite(retrievedAt))return Response.json({error:"Invalid report source"},{status:400});
    seen.add(source.evidence_id);sources.push({...source,publishedAt,retrievedAt});
  }
  const db=(env as unknown as {DB:D1Database}).DB,statements=[db.prepare(`INSERT INTO reports(id,slug,title,type,summary,body,country,ai_generated,published_at,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)`).bind(id,slug,body.title,body.type,body.summary,body.body,body.country,Number(body.aiGenerated!==false),now.getTime(),now.getTime())];
  for(const source of sources)statements.push(db.prepare(`INSERT INTO report_sources(id,report_id,evidence_id,document_id,source_type,title,url,publisher,published_at,retrieved_at) VALUES(?,?,?,?,?,?,?,?,?,?)`).bind(crypto.randomUUID(),id,source.evidence_id,source.document_id||null,source.source_type,source.title,source.url,source.publisher,source.publishedAt,source.retrievedAt));
  await db.batch(statements);
  return Response.json({ ok: true, slug });
}

export async function GET(request: Request) {
  const params = new URL(request.url).searchParams, filters = [];
  const type = params.get("type"), country = params.get("country"), slug = params.get("slug");
  if (type && types.has(type)) filters.push(eq(reports.type, type as "daily"));
  if (country && countries.has(country)) filters.push(eq(reports.country, country as "KZ"));
  if (slug) filters.push(eq(reports.slug, slug));
  try {
    const selected = await getDb().select().from(reports).where(filters.length ? and(...filters) : undefined).orderBy(desc(reports.publishedAt)).limit(slug ? 1 : 100);
    const rows = selected.filter(report => !supersededSlugs.has(report.slug));
    const sources=slug&&rows[0]?await getDb().select().from(reportSources).where(eq(reportSources.reportId,rows[0].id)).orderBy(reportSources.evidenceId):[];
    return Response.json({ records: rows, count: rows.length, sources });
  } catch { return Response.json({ records: [], count: 0, fallback: true }); }
}

export async function DELETE(request: Request) {
  if (!authorized(request)) return Response.json({ error: "Unauthorized" }, { status: 401 });
  const slug = new URL(request.url).searchParams.get("slug")?.trim();
  if (!slug) return Response.json({ error: "Missing slug" }, { status: 400 });
  const db=(env as unknown as {DB:D1Database}).DB;
  const found=await db.prepare("SELECT id FROM reports WHERE slug = ? LIMIT 1").bind(slug).first<{id:string}>();
  if(!found) return Response.json({error:"Report not found"},{status:404});
  await db.batch([
    db.prepare("DELETE FROM report_sources WHERE report_id = ?").bind(found.id),
    db.prepare("DELETE FROM reports WHERE id = ?").bind(found.id),
  ]);
  return Response.json({ok:true,slug});
}
