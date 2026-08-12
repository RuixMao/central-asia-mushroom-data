import { and, desc, eq, gte, lt } from "drizzle-orm";
import { getDb } from "../../../../db";
import { dataSnapshots, reports } from "../../../../db/schema";
import { getChatGPTUser } from "../../../chatgpt-auth";

export const dynamic = "force-dynamic";
type PriceData = { variety?:string; form?:string; spec?:string; channel?:string; price_local?:number; currency?:string; price_cny?:number; observed_at?:string; source_url?:string; status?:string; reason?:string };
const chinaDate=()=>new Intl.DateTimeFormat("en-CA",{timeZone:"Asia/Shanghai",year:"numeric",month:"2-digit",day:"2-digit"}).format(new Date());
const plain=(value:string)=>value.replace(/[#*_>`~-]/g," ").replace(/\s+/g," ").trim();

export async function POST(){
  if(!await getChatGPTUser()) return Response.json({error:"请先登录后生成日报"},{status:401});
  const apiKey=process.env.AI_API_KEY;
  if(!apiKey) return Response.json({error:"DeepSeek 密钥尚未配置"},{status:503});
  const date=chinaDate(), start=new Date(`${date}T00:00:00+08:00`), end=new Date(start.getTime()+86400000);
  const snapshots=await getDb().select().from(dataSnapshots).where(and(eq(dataSnapshots.metric,"price_retail"),gte(dataSnapshots.capturedAt,start),lt(dataSnapshots.capturedAt,end))).orderBy(desc(dataSnapshots.capturedAt)).limit(500);
  const prices=snapshots.filter(row=>{const data=row.data as PriceData;return data.status==="live"&&data.price_local!=null});
  const gaps=snapshots.filter(row=>(row.data as PriceData).status==="gap");
  if(!prices.length) return Response.json({error:`${date} 尚无可用价格，需先完成今日价格采集`,priceCount:0,gapCount:gaps.length},{status:409});
  const context=prices.map(row=>({country:row.country,source:row.source,...row.data as PriceData}));
  const prompt=`你是中亚食用菌市场分析师。仅依据给定的今日价格记录生成中文日报，不得虚构成交价、涨跌幅或缺失数据。\n日期：${date}\n价格记录（共 ${context.length} 条）：\n${JSON.stringify(context)}\n要求：标题为“中亚菌类价格日报｜${date}”；先写不超过40字导读；正文包括“今日价格全景”“国家与渠道观察”“商机提示”；覆盖输入中的全部价格，可合并同国同品类价格带但不能遗漏国家；给出2至3条可执行建议；注明挂牌/页面观察价不等于成交价；输出 Markdown，500至900字。`;
  const response=await fetch(`${(process.env.AI_BASE_URL||"https://api.deepseek.com").replace(/\/$/,"")}/chat/completions`,{method:"POST",headers:{"content-type":"application/json",authorization:`Bearer ${apiKey}`},body:JSON.stringify({model:process.env.AI_MODEL||"deepseek-chat",messages:[{role:"user",content:prompt}],temperature:.2,stream:false})});
  if(!response.ok){console.error("DeepSeek generation failed",response.status,(await response.text()).slice(0,500));return Response.json({error:"DeepSeek 生成失败，请稍后重试"},{status:502})}
  const result=await response.json() as {choices?:Array<{message?:{content?:string}}>};
  const body=result.choices?.[0]?.message?.content?.trim();
  if(!body) return Response.json({error:"DeepSeek 未返回日报内容"},{status:502});
  const title=`中亚菌类价格日报｜${date}`,id=crypto.randomUUID(),slug=`${date}-central-asia-mushroom-price-${id.slice(0,6)}`,now=new Date();
  await getDb().insert(reports).values({id,slug,title,type:"daily",summary:plain(body).slice(0,200),body,country:"KZ",aiGenerated:true,publishedAt:now,createdAt:now});
  return Response.json({ok:true,id,slug,title,body,priceCount:prices.length,gapCount:gaps.length,aiGenerated:true,generatedBy:"deepseek"});
}
