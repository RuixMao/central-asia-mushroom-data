import { and, desc, eq, gte, lt } from "drizzle-orm";
import { getDb } from "../../../../db";
import { dataSnapshots, marketDocuments, priceObservations, products, platforms, reportSources, reports } from "../../../../db/schema";
import { getChatGPTUser } from "../../../chatgpt-auth";

export const dynamic="force-dynamic";
const countries={KZ:"哈萨克斯坦",UZ:"乌兹别克斯坦",KG:"吉尔吉斯斯坦",TJ:"塔吉克斯坦",TM:"土库曼斯坦"} as const;
const species:Record<string,string>={button_mushroom:"双孢菇",oyster_mushroom:"平菇",shiitake:"香菇",enoki:"金针菇",king_oyster_mushroom:"杏鲍菇",wood_ear:"木耳",shimeji:"真姬菇",porcini:"牛肝菌",chanterelle:"鸡油菌",morel:"羊肚菌",truffle:"松露"};
const speciesHs:Record<string,string>={button_mushroom:"070951",oyster_mushroom:"070959",shiitake:"070959",king_oyster_mushroom:"070959",enoki:"070959",wood_ear:"070959",shimeji:"070959",porcini:"070959",chanterelle:"070959",morel:"070959",truffle:"070959"};
const forms:Record<string,string>={fresh:"鲜品",chilled:"冷藏",frozen:"冷冻",dried:"干制",pickled:"腌渍",canned:"罐装",powder:"粉剂"};
const chinaDate=()=>new Intl.DateTimeFormat("en-CA",{timeZone:"Asia/Shanghai",year:"numeric",month:"2-digit",day:"2-digit"}).format(new Date());
const plain=(value:string)=>value.replace(/[#*_>`~-]/g," ").replace(/\s+/g," ").trim();
const median=(values:number[])=>{const rows=[...values].sort((a,b)=>a-b),mid=Math.floor(rows.length/2);return rows.length?rows.length%2?rows[mid]:(rows[mid-1]+rows[mid])/2:null};
const forbidden=/https?:\/\/|(?:price|observed|source)\s*[_-]\s*(?:usd|local|cny|at|url)|\b(?:AI|API|JSON|LLM|GPT|ChatGPT|DeepSeek|SQL|D1|null|live|gap|prompt|price_retail)\b|人工智能|大模型|语言模型|模型生成|智能生成|自动生成|机器生成|算法生成|数据库|字段|代码|键值|请求|响应|自动采集|采集管线|采集|抓取|爬虫|入库|接口|算法|历史序列不足|暂不判断|暂不提供|暂未直接|数据不足|无足够数据|样本不足|样本量|判断不了|无法判断|不判断涨跌/iu;
const sections=["核心观点","市场变化与驱动","商业含义","关注事项","数据口径与风险"];
const customerSafe=(body:string,allowed:Set<string>)=>{const normalized=body.normalize("NFKC"),refs=[...normalized.matchAll(/\[(S\d+)\]/g)].map(match=>match[1]);return normalized.length>=900&&normalized.length<=4200&&!normalized.includes("```")&&!normalized.includes("中亚菌类价格日报｜")&&!forbidden.test(normalized)&&sections.every(section=>normalized.split(section).length===2)&&refs.every(ref=>allowed.has(ref))};
const summaryFrom=(body:string)=>plain(body.split(/\n\s*\n/).find(block=>block.trim()&&!/^#{1,6}\s/.test(block.trim()))??body).slice(0,200);
const packageLabel=(value:number|null,unit:string|null)=>value&&unit?`${Number(value.toFixed(3))} ${unit}`:"规格待核验";
const escapeCell=(value:unknown)=>String(value??"—").replace(/\|/g,"/").replace(/\r?\n/g," ").trim();

export async function POST(){
 if(!await getChatGPTUser())return Response.json({error:"请先登录后生成日报"},{status:401});
 const apiKey=process.env.AI_API_KEY;if(!apiKey)return Response.json({error:"报告生成服务尚未配置"},{status:503});
 const date=chinaDate(),start=new Date(`${date}T00:00:00+08:00`),end=new Date(start.getTime()+86400000),historyStart=new Date(start.getTime()-30*86400000);
 const rows=await getDb().select({price:priceObservations,product:products,platform:platforms}).from(priceObservations).innerJoin(products,eq(priceObservations.productId,products.id)).innerJoin(platforms,eq(products.platformId,platforms.id)).where(and(gte(priceObservations.observedAt,historyStart),lt(priceObservations.observedAt,end),eq(priceObservations.validationStatus,"valid"),eq(products.classificationStatus,"classified"))).orderBy(desc(priceObservations.observedAt)).limit(1000);
 const today=rows.filter(row=>row.price.observationDate===date&&row.price.currentPrice!=null&&row.price.normalizedQuantityKg&&row.price.usdRateLocalPerUsd&&row.product.speciesId);
 if(!today.length)return Response.json({error:`${date} 尚无可比较的标准化价格，需先完成今日价格采集`,priceCount:0},{status:409});
 const dedup=new Map(today.map(row=>[`${row.product.id}|${row.price.observationDate}`,row])),current=[...dedup.values()];
 const table=["| 国家 | 品类（中文/原文） | 渠道（中文/原名） | 形态与规格 | 当地挂牌价 | 折合美元/公斤 | 观察日期 |","|---|---|---|---|---:|---:|---|",...current.map(row=>{const usdKg=(row.price.normalizedPricePerKg??0)/(row.price.usdRateLocalPerUsd??1);return `| ${countries[row.product.country as keyof typeof countries]??row.product.country} | ${species[row.product.speciesId!]??"食用菌"}（${escapeCell(row.product.originalTitle)}） | 当地零售渠道（${escapeCell(row.platform.name)}） | ${forms[row.product.productForm]??row.product.productForm}；${packageLabel(row.price.packageValue,row.price.packageUnit)} | ${row.price.currentPrice} ${row.price.currency} | ${usdKg.toFixed(2)} | ${row.price.observationDate} |`})].join("\n");
 const groups=new Map<string,{country:string;speciesId:string;values:Map<string,number[]>}>();
 for(const row of rows){if(!row.product.speciesId||!row.price.normalizedPricePerKg||!row.price.usdRateLocalPerUsd)continue;const key=`${row.product.country}|${row.product.speciesId}|${row.product.productForm}`,group=groups.get(key)??{country:row.product.country,speciesId:row.product.speciesId,values:new Map()};const values=group.values.get(row.price.observationDate)??[];values.push(row.price.normalizedPricePerKg/row.price.usdRateLocalPerUsd);group.values.set(row.price.observationDate,values);groups.set(key,group)}
 const trends=[...groups.values()].map(group=>{const days=[...group.values].sort(([a],[b])=>b.localeCompare(a)),latest=median(days[0]?.[1]??[]),previous=median(days.find(([day])=>day<date)?.[1]??[]);return {国家:countries[group.country as keyof typeof countries]??group.country,品类:species[group.speciesId]??group.speciesId,有效日期数:days.length,最新美元每公斤:latest==null?null:Number(latest.toFixed(2)),较前次可比变化:days.length>=3&&latest!=null&&previous!=null?`${((latest/previous-1)*100).toFixed(1)}%`:null}});
 // 年度进口单价（贸易口径，UN Comtrade）历史序列：零售序列不足时作年度趋势参考
 const tradeRows=await getDb().select().from(dataSnapshots).where(eq(dataSnapshots.metric,"trade")).orderBy(desc(dataSnapshots.capturedAt)).limit(500);
 const annualByCountryHs=new Map<string,Map<string,number>>();
 for(const row of tradeRows){const d=row.data as Record<string,unknown>;if(d.status!=="live"||d.period_type==="monthly")continue;const year=String(d.year??""),unit=d.unit_price_usd_kg,hs=String(d.hs??"");if(year&&typeof unit==="number"&&hs){const m=annualByCountryHs.get(`${row.country}|${hs}`)??new Map<string,number>();m.set(year,unit);annualByCountryHs.set(`${row.country}|${hs}`,m)}}
 const annualRef=[...groups.values()].map(group=>{const hs=speciesHs[group.speciesId??""],seq=hs?annualByCountryHs.get(`${group.country}|${hs}`):undefined;if(!seq||seq.size<2)return null;const years=[...seq.keys()].sort(),first=seq.get(years[0])!,last=seq.get(years[years.length-1])!;return {国家:countries[group.country as keyof typeof countries]??group.country,品类:species[group.speciesId]??group.speciesId,贸易口径年度进口单价USD每公斤:Object.fromEntries([...seq].sort(([a],[b])=>a.localeCompare(b))),多年变化:first?`${((last/first-1)*100).toFixed(1)}%`:null}}).filter(Boolean);
 const documents=await getDb().select().from(marketDocuments).where(and(eq(marketDocuments.verificationStatus,"verified"),gte(marketDocuments.publishedAt,new Date(start.getTime()-90*86400000)))).orderBy(desc(marketDocuments.relevanceScore),desc(marketDocuments.publishedAt)).limit(25);
 const evidence=documents.map((item,index)=>({id:`S${index+1}`,document:item,context:{证据编号:`S${index+1}`,国家:countries[item.country as keyof typeof countries],类型:item.kind,标题:item.title,发布机构:item.publisher,发布日期:item.publishedAt.toISOString().slice(0,10),事实摘要:item.excerpt}})),allowed=new Set(evidence.map(item=>item.id));
 const prompt=`你是因恒科技的中亚食用菌首席市场研究员。请写一份面向进口商、渠道商、投资人与经营管理层的中文市场日报。采用国际机构研究简报常见的表达方式：核心判断置前，随后解释变化、驱动、商业含义与风险边界。语言克制、连贯、简洁，不使用营销口号或机械审计标签。只可使用下方价格、历史序列和证据包，不得自行补充新闻、政策、数字、来源、因果或预测。\n日期：${date}\n价格表由系统确定性生成，正文不要抄写全部数字，只分析结构：\n${table}\n同口径零售历史序列：${JSON.stringify(trends)}\n年度进口单价参考（贸易口径，UN Comtrade）：${JSON.stringify(annualRef)}\n已核验政策/新闻/宏观证据包：${JSON.stringify(evidence.map(item=>item.context))}\n\n成稿要求：\n1. 页面标题另行显示。先写60至100字导读；随后恰好使用“核心观点”“市场变化与驱动”“商业含义”“关注事项”“数据口径与风险”五个二级标题。\n2. “核心观点”用3条短句概括最重要结论；其余部分使用连贯段落，不给每句话添加【事实】【研判】【情景】标签，不重复“今日动作”。\n3. 观点明确但不夸张，先写结论再解释证据和驱动，清楚区分观察、判断与条件情景；避免命令式、口号式和模板化语言。\n4. 政策或新闻事实必须引用 [S1] 形式的证据编号，且只能使用证据包存在的编号。没有材料时简洁说明“本期未纳入可核验的新材料”，不要逐国重复。\n5. 零售趋势只使用有效日期数不少于3的同口径序列；不足3期的品类可用“年度进口单价参考（贸易口径）”描述年度走势，并注明其不是零售价；两种依据均不足的品类不写趋势。禁止出现“历史序列不足”“暂不判断”“数据不足”“无法判断”等表述。\n6. “商业含义”分别说明对产能方、渠道商或投资者的意义；“关注事项”给出3至5条有触发条件和风险边界的观察清单。公开页面挂牌价不等于实际成交价。\n7. 政策信号只陈述可核验事实。不得出现任何生成方式、内部系统、技术字段或流程词。输出1000至1800字 Markdown 正文，不附来源清单或网址。`;
 let analysis="";
 for(let attempt=0;attempt<2;attempt++){
  const request=attempt?`${prompt}\n\n上一稿未通过发布检查。请仅使用允许的证据编号，保留五个指定栏目，以连贯、克制的机构研究语言完整重写。`:prompt;
  const response=await fetch(`${(process.env.AI_BASE_URL||"https://api.deepseek.com").replace(/\/$/,"")}/chat/completions`,{method:"POST",headers:{"content-type":"application/json",authorization:`Bearer ${apiKey}`},body:JSON.stringify({model:process.env.AI_MODEL||"deepseek-chat",messages:[{role:"user",content:request}],temperature:.15,stream:false})});
  if(!response.ok){console.error("Report generation failed",response.status,(await response.text()).slice(0,500));if(attempt===1)return Response.json({error:"日报生成失败，请稍后重试"},{status:502});continue}
  const result=await response.json() as {choices?:Array<{message?:{content?:string}}>};analysis=result.choices?.[0]?.message?.content?.trim()??"";if(customerSafe(analysis,allowed))break;
 }
 if(!customerSafe(analysis,allowed))return Response.json({error:"日报未通过研究成稿检查，请重新生成"},{status:502});
 const usedIds=new Set([...analysis.matchAll(/\[(S\d+)\]/g)].map(match=>match[1])),usedEvidence=evidence.filter(item=>usedIds.has(item.id));
 const sourceList=usedEvidence.length?`\n\n## 来源与资料日期\n${usedEvidence.map(item=>`- [${item.id}] [${escapeCell(item.document.publisher)}：${escapeCell(item.document.title)}](${item.document.sourceUrl})（${item.document.publishedAt.toISOString().slice(0,10)}，检索于 ${item.document.retrievedAt.toISOString().slice(0,10)}）`).join("\n")}`:"\n\n## 来源与资料日期\n- 本期未纳入可核验的新增政策与新闻材料，相关部分不作外推。";
 const body=`${analysis}\n\n## 今日价格全景\n${table}${sourceList}`,title=`中亚菌类市场研究日报｜${date}`,id=crypto.randomUUID(),slug=`${date}-central-asia-mushroom-research-${id.slice(0,6)}`,now=new Date();
 await getDb().insert(reports).values({id,slug,title,type:"daily",summary:summaryFrom(body),body,country:"KZ",aiGenerated:true,publishedAt:now,createdAt:now});
 if(usedEvidence.length)await getDb().insert(reportSources).values(usedEvidence.map(item=>({id:crypto.randomUUID(),reportId:id,evidenceId:item.id,documentId:item.document.id,sourceType:item.document.kind,title:item.document.title,url:item.document.sourceUrl,publisher:item.document.publisher,publishedAt:item.document.publishedAt,retrievedAt:item.document.retrievedAt})));
 return Response.json({ok:true,id,slug,title,body,priceCount:current.length,evidenceCount:usedEvidence.length,trendGroups:trends.length});
}
