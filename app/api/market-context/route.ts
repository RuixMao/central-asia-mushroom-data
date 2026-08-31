import { and, desc, eq, gte } from "drizzle-orm";
import { getDb } from "../../../db";
import { marketDocuments } from "../../../db/schema";
import { targetMarketCodes } from "../../market-scope";

const countries=new Set<string>(targetMarketCodes),kinds=new Set(["news","policy","macro"]);

export async function GET(request:Request){
 const params=new URL(request.url).searchParams,filters=[];
 const country=params.get("country"),kind=params.get("kind"),days=Math.min(Math.max(Number(params.get("days")??90),1),730);
 if(country&&countries.has(country))filters.push(eq(marketDocuments.country,country as "KZ"));
 if(kind&&kinds.has(kind))filters.push(eq(marketDocuments.kind,kind as "news"));
 filters.push(eq(marketDocuments.verificationStatus,"verified"));
 filters.push(gte(marketDocuments.publishedAt,new Date(Date.now()-days*86400000)));
 const records=await getDb().select().from(marketDocuments).where(and(...filters)).orderBy(desc(marketDocuments.publishedAt)).limit(100);
 return Response.json({records,count:records.length});
}
