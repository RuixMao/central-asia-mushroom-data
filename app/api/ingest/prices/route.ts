import { env } from "cloudflare:workers";

const authorized=(request:Request)=>Boolean(process.env.CRON_SECRET)&&request.headers.get("x-cron-secret")===process.env.CRON_SECRET;
type Item={platform:string;platform_name:string;platform_product_id:string;country:string;city:string;collection_point_id:string;product_url:string;original_title:string;original_description?:string;original_category?:string;original_language?:string;species_id:string|null;product_form:string;classification_status:string;classification_confidence:number;classification_evidence:Record<string,unknown>;observed_at:string;observation_date:string;current_price:number;regular_price?:number|null;promotion_price?:number|null;currency:string;package_value?:number|null;package_unit?:string|null;normalized_quantity_kg?:number|null;normalized_price_per_kg?:number|null;price_usd?:number|null;usd_rate_local_per_usd?:number|null;fx_source?:string|null;fx_timestamp?:string|null;in_stock?:boolean|null;raw_price_text?:string|null;source_type:string;page_fingerprint?:string|null;validation_status:string;review_reasons?:string[];sanity_outlier?:boolean;sanity_reason?:string|null};
export async function POST(request:Request){
 if(!authorized(request))return Response.json({error:"Unauthorized"},{status:401});
 const body=await request.json() as {items?:Item[]};if(!body.items?.length)return Response.json({error:"items required"},{status:400});
 const expected:Record<string,Set<string>>={KZ:new Set(["KZT"]),UZ:new Set(["UZS"]),KG:new Set(["KGS"]),TJ:new Set(["TJS"]),TM:new Set(["TMT"]),LA:new Set(["LAK"]),VN:new Set(["VND"]),TH:new Set(["THB"]),MM:new Set(["MMK"]),KH:new Set(["KHR","USD"])};
 const allowed=new Set(["KZT","UZS","KGS","TJS","TMT","LAK","VND","THB","MMK","KHR","USD"]);
 const timezones:Record<string,string>={KZ:"Asia/Almaty",UZ:"Asia/Tashkent",KG:"Asia/Bishkek",TJ:"Asia/Dushanbe",TM:"Asia/Ashgabat",LA:"Asia/Vientiane",VN:"Asia/Ho_Chi_Minh",TH:"Asia/Bangkok",MM:"Asia/Yangon",KH:"Asia/Phnom_Penh"};
 const db=(env as unknown as {DB:D1Database}).DB,now=Date.now();let written=0,rejected=0,deleted=0,filtered=0;const skipped=0;const errors:{index:number;reason:string}[]=[];
 // 正式库采用准入制。历史遗留的待复核/拒绝价格及其零售快照不再保留；
 // 失败原因仍存在于采集审计和 source_health 质量统计中。
 const cleanup=await db.batch([
  db.prepare("DELETE FROM price_observations WHERE validation_status <> 'valid'"),
  db.prepare("DELETE FROM data_snapshots WHERE metric='price_retail' AND json_extract(data,'$.validation_status') IS NOT NULL AND json_extract(data,'$.validation_status') <> 'valid'")
 ]);
 deleted+=cleanup.reduce((sum,result)=>sum+(result.meta.changes??0),0);
 for(const [index,x] of body.items.entries()){
  const productId=`${x.platform}:${x.collection_point_id}:${x.platform_product_id}`;
  if(x.validation_status!=="valid"){
   // 同一商品当天若先前曾被错误放行，本轮复核不通过时立即撤回。
   if(x.platform&&x.collection_point_id&&x.platform_product_id&&x.observation_date){
    const result=await db.prepare("DELETE FROM price_observations WHERE product_id=? AND observation_date=?").bind(productId,x.observation_date).run();
    deleted+=result.meta.changes??0;
   }
   filtered++;continue;
  }
  const reason=!x.platform||!x.platform_product_id||!x.product_url||!x.original_title||!x.country||!x.city?"missing required field":!allowed.has(x.currency)?"illegal currency":x.current_price==null||x.current_price<=0?"price must be positive":expected[x.country]&&!expected[x.country].has(x.currency)?"currency-country mismatch":null;
  if(reason){rejected++;errors.push({index,reason});continue}
  try{
   const stmts=[
    db.prepare("INSERT INTO platforms(id,name,country,collection_method,status,updated_at) VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET status=excluded.status,updated_at=excluded.updated_at").bind(x.platform,x.platform_name,x.country,x.source_type,"active",now),
    db.prepare("INSERT INTO collection_points(id,country,city,platform_id,timezone,active,public_label) VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET active=1").bind(x.collection_point_id,x.country,x.city,x.platform,timezones[x.country]??"UTC",1,x.city),
    db.prepare("INSERT INTO products(id,platform_id,platform_product_id,collection_point_id,country,city,product_url,original_title,original_description,original_category,original_language,species_id,product_form,classification_status,classification_confidence,classification_evidence,first_seen_at,last_seen_at,active) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(platform_id,collection_point_id,platform_product_id) DO UPDATE SET product_url=excluded.product_url,original_title=excluded.original_title,species_id=excluded.species_id,product_form=excluded.product_form,classification_status=excluded.classification_status,classification_confidence=excluded.classification_confidence,classification_evidence=excluded.classification_evidence,last_seen_at=excluded.last_seen_at,active=1").bind(productId,x.platform,x.platform_product_id,x.collection_point_id,x.country,x.city,x.product_url,x.original_title,x.original_description??null,x.original_category??null,x.original_language??null,x.species_id,x.product_form,x.classification_status,x.classification_confidence,JSON.stringify(x.classification_evidence),now,now,1),
    db.prepare("INSERT INTO price_observations(id,product_id,observed_at,observation_date,current_price,regular_price,promotion_price,currency,package_value,package_unit,normalized_quantity_kg,normalized_price_per_kg,price_usd,usd_rate_local_per_usd,fx_source,fx_timestamp,in_stock,raw_price_text,source_url,source_type,page_fingerprint,collection_status,validation_status,validation_errors,sanity_outlier,sanity_reason,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(product_id,observation_date) DO UPDATE SET observed_at=excluded.observed_at,current_price=excluded.current_price,regular_price=excluded.regular_price,promotion_price=excluded.promotion_price,currency=excluded.currency,package_value=excluded.package_value,package_unit=excluded.package_unit,normalized_quantity_kg=excluded.normalized_quantity_kg,normalized_price_per_kg=excluded.normalized_price_per_kg,price_usd=excluded.price_usd,usd_rate_local_per_usd=excluded.usd_rate_local_per_usd,fx_source=excluded.fx_source,fx_timestamp=excluded.fx_timestamp,in_stock=excluded.in_stock,raw_price_text=excluded.raw_price_text,source_url=excluded.source_url,source_type=excluded.source_type,page_fingerprint=excluded.page_fingerprint,collection_status=excluded.collection_status,validation_status=excluded.validation_status,validation_errors=excluded.validation_errors,sanity_outlier=excluded.sanity_outlier,sanity_reason=excluded.sanity_reason").bind(`${x.platform}:${x.platform_product_id}:${x.observation_date}`,productId,new Date(x.observed_at).getTime(),x.observation_date,x.current_price,x.regular_price??null,x.promotion_price??null,x.currency,x.package_value??null,x.package_unit??null,x.normalized_quantity_kg??null,x.normalized_price_per_kg??null,x.price_usd??null,x.usd_rate_local_per_usd??null,x.fx_source??null,x.fx_timestamp??null,x.in_stock==null?null:Number(x.in_stock),x.raw_price_text??null,x.product_url,x.source_type,x.page_fingerprint??null,"collected",x.validation_status,JSON.stringify(x.review_reasons??[]),Number(Boolean(x.sanity_outlier)),x.sanity_reason??null,now)
   ];
   // species 字典表只收录已识别的物种（species.id 为主键，NULL 会违反 NOT NULL）；
   // 分类 unknown 的商品（species_id 为 null）跳过字典写入，products.species_id 列本身允许 null。
   if(x.species_id){stmts.unshift(db.prepare("INSERT INTO species(id,name_zh,name_en,dictionary_version,review_status) VALUES(?,?,?,?,?) ON CONFLICT(id) DO NOTHING").bind(x.species_id,x.species_id,x.species_id,"v1","seeded"));}
   await db.batch(stmts);written++;}catch(error){rejected++;errors.push({index,reason:error instanceof Error?error.message:"database write failed"});}
 }
 return Response.json({ok:true,written,updated:0,skipped,filtered,deleted,rejected,errors});
}
