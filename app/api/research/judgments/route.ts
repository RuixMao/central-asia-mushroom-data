import { and, desc, eq } from "drizzle-orm";
import { getDb } from "../../../../db";
import { researchJudgments } from "../../../../db/schema";

const frequencies=new Set(["daily","weekly","monthly","quarterly","annual"]);
const statuses=new Set(["open","confirmed","partially_confirmed","rejected","expired"]);
const authorized=(request:Request)=>Boolean(process.env.CRON_SECRET)&&request.headers.get("x-cron-secret")===process.env.CRON_SECRET;

export async function GET(request:Request){
 if(!authorized(request))return Response.json({error:"Unauthorized"},{status:401});
 const params=new URL(request.url).searchParams,filters=[];
 if(params.get("frequency")&&frequencies.has(params.get("frequency")!))filters.push(eq(researchJudgments.frequency,params.get("frequency") as "daily"));
 if(params.get("period_key"))filters.push(eq(researchJudgments.periodKey,params.get("period_key")!));
 if(params.get("status")&&statuses.has(params.get("status")!))filters.push(eq(researchJudgments.status,params.get("status") as "open"));
 if(params.get("country"))filters.push(eq(researchJudgments.country,params.get("country")!));
 const records=await getDb().select().from(researchJudgments).where(filters.length?and(...filters):undefined).orderBy(desc(researchJudgments.createdAt)).limit(500);
 return Response.json({records,count:records.length});
}

export async function POST(request:Request){
 if(!authorized(request))return Response.json({error:"Unauthorized"},{status:401});
 const body=await request.json() as {frequency?:string;period_key?:string;country?:string;species_id?:string;judgment?:string;evidence?:Record<string,unknown>[];expected_by?:string;source_report_id?:string};
 if(!body.frequency||!frequencies.has(body.frequency)||!body.period_key||!body.judgment||!Array.isArray(body.evidence))return Response.json({error:"Invalid judgment"},{status:400});
 const now=new Date(),id=crypto.randomUUID();
 await getDb().insert(researchJudgments).values({id,frequency:body.frequency as "daily",periodKey:body.period_key,country:body.country??null,speciesId:body.species_id??null,judgment:body.judgment,evidence:body.evidence,expectedBy:body.expected_by??null,status:"open",sourceReportId:body.source_report_id??null,createdAt:now,updatedAt:now});
 return Response.json({ok:true,id});
}

export async function PATCH(request:Request){
 if(!authorized(request))return Response.json({error:"Unauthorized"},{status:401});
 const body=await request.json() as {id?:string;status?:string;outcome?:string;impact?:string};
 if(!body.id||!body.status||!statuses.has(body.status))return Response.json({error:"Invalid judgment update"},{status:400});
 const now=new Date();
 await getDb().update(researchJudgments).set({status:body.status as "open",outcome:body.outcome??null,impact:body.impact??null,resolvedAt:body.status==="open"?null:now,updatedAt:now}).where(eq(researchJudgments.id,body.id));
 return Response.json({ok:true,id:body.id});
}
