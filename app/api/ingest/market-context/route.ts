import { env } from "cloudflare:workers";

const countries=new Set(["KZ","UZ","KG","TJ","TM"]),kinds=new Set(["news","policy","macro"]);
const authorized=(request:Request)=>Boolean(process.env.CRON_SECRET)&&request.headers.get("x-cron-secret")===process.env.CRON_SECRET;
type Document={id?:string;country?:string;kind?:string;title?:string;publisher?:string;source_url?:string;language?:string;published_at?:string;retrieved_at?:string;excerpt?:string;primary_source?:boolean;verification_status?:string;relevance_score?:number;content_hash?:string};

export async function POST(request:Request){
 if(!authorized(request))return Response.json({error:"Unauthorized"},{status:401});
 const payload=await request.json() as {documents?:Document[]};
 if(!payload.documents?.length)return Response.json({error:"documents required"},{status:400});
 const db=(env as unknown as {DB:D1Database}).DB,now=Date.now();let written=0,rejected=0;const errors:{index:number;reason:string}[]=[];
 for(const [index,item] of payload.documents.entries()){
  const published=Date.parse(item.published_at??""),retrieved=Date.parse(item.retrieved_at??"");
  const reason=!countries.has(item.country??"")?"invalid country":!kinds.has(item.kind??"")?"invalid kind":!item.title||!item.publisher||!item.source_url||!item.excerpt?"missing required field":!Number.isFinite(published)||!Number.isFinite(retrieved)?"invalid timestamp":null;
  if(reason){rejected++;errors.push({index,reason});continue}
  try{
   await db.prepare(`INSERT INTO market_documents(id,country,kind,title,publisher,source_url,language,published_at,retrieved_at,excerpt,primary_source,verification_status,relevance_score,content_hash,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(source_url) DO UPDATE SET title=excluded.title,publisher=excluded.publisher,published_at=excluded.published_at,retrieved_at=excluded.retrieved_at,excerpt=excluded.excerpt,primary_source=excluded.primary_source,verification_status=excluded.verification_status,relevance_score=excluded.relevance_score,content_hash=excluded.content_hash`).bind(item.id??crypto.randomUUID(),item.country,item.kind,item.title,item.publisher,item.source_url,item.language??"und",published,retrieved,item.excerpt,Number(Boolean(item.primary_source)),item.verification_status??"discovered",item.relevance_score??0,item.content_hash??"",now).run();written++;
  }catch(error){rejected++;errors.push({index,reason:error instanceof Error?error.message:"write failed"})}
 }
 return Response.json({ok:true,written,rejected,errors});
}
