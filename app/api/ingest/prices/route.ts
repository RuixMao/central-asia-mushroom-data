import { env } from "cloudflare:workers";
import scope from "../../../../scope.json";

const authorized=(request:Request)=>Boolean(process.env.CRON_SECRET)&&request.headers.get("x-cron-secret")===process.env.CRON_SECRET;
type Item={platform:string;platform_name:string;platform_product_id:string;country:string;city:string;collection_point_id:string;product_url:string;original_title:string;original_description?:string;original_category?:string;original_language?:string;species_id:string|null;product_form:string;classification_status:string;classification_confidence:number;classification_evidence:Record<string,unknown>;observed_at:string;observation_date:string;current_price:number;regular_price?:number|null;promotion_price?:number|null;currency:string;package_value?:number|null;package_unit?:string|null;normalized_quantity_kg?:number|null;normalized_price_per_kg?:number|null;price_usd?:number|null;usd_rate_local_per_usd?:number|null;fx_source?:string|null;fx_timestamp?:string|null;in_stock?:boolean|null;raw_price_text?:string|null;source_type:string;page_fingerprint?:string|null;validation_status:string;review_reasons?:string[];sanity_outlier?:boolean;sanity_reason?:string|null;status?:"active"|"archived"|"deleted";valid_until?:string|null};
const countries=new Map(scope.countries.map(country=>[country.code,country]));
const species=new Set(scope.species.map(item=>item.slug));
export async function POST(request:Request){
 if(!authorized(request))return Response.json({error:"Unauthorized"},{status:401});
 const body=await request.json() as {items?:Item[]};if(!body.items?.length)return Response.json({error:"items required"},{status:400});
 const db=(env as unknown as {DB:D1Database}).DB,now=Date.now();let written=0,rejected=0;const deleted=0,filtered=0,skipped=0;const errors:{index:number;reason:string}[]=[];
 for(const [index,x] of body.items.entries()){
  const productId=`${x.platform}:${x.collection_point_id}:${x.platform_product_id}`;
  const market=countries.get(x.country);
  const accepted=market?new Set([market.currency,...("accepted_currencies" in market?(market.accepted_currencies??[]):[])]):new Set<string>();
  const reason=!x.platform||!x.platform_product_id||!x.product_url||!x.original_title||!x.country||!x.city?"missing required field":!market?"country is not in scope.json":!x.species_id||!species.has(x.species_id)?"species is not in scope.json":!accepted.has(x.currency)?"currency-country mismatch":!Number.isFinite(x.current_price)||x.current_price<=0||x.current_price>1_000_000_000_000?"price must be a plausible positive number":null;
  if(reason){rejected++;errors.push({index,reason});continue}
  try{
   const stmts=[
    db.prepare("INSERT INTO platforms(id,name,country,collection_method,status,updated_at) VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET status=excluded.status,updated_at=excluded.updated_at").bind(x.platform,x.platform_name,x.country,x.source_type,"active",now),
    db.prepare("INSERT INTO collection_points(id,country,city,platform_id,timezone,active,public_label) VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET active=1").bind(x.collection_point_id,x.country,x.city,x.platform,market.timezone,1,x.city),
    db.prepare("INSERT INTO products(id,platform_id,platform_product_id,collection_point_id,country,city,product_url,original_title,original_description,original_category,original_language,species_id,product_form,classification_status,classification_confidence,classification_evidence,first_seen_at,last_seen_at,active) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(platform_id,collection_point_id,platform_product_id) DO UPDATE SET product_url=excluded.product_url,original_title=excluded.original_title,species_id=excluded.species_id,product_form=excluded.product_form,classification_status=excluded.classification_status,classification_confidence=excluded.classification_confidence,classification_evidence=excluded.classification_evidence,last_seen_at=excluded.last_seen_at,active=1").bind(productId,x.platform,x.platform_product_id,x.collection_point_id,x.country,x.city,x.product_url,x.original_title,x.original_description??null,x.original_category??null,x.original_language??null,x.species_id,x.product_form,x.classification_status,x.classification_confidence,JSON.stringify(x.classification_evidence),now,now,1),
    db.prepare("INSERT INTO price_observations(id,product_id,country,species_id,status,valid_until,observed_at,observation_date,current_price,regular_price,promotion_price,currency,package_value,package_unit,normalized_quantity_kg,normalized_price_per_kg,price_usd,usd_rate_local_per_usd,fx_source,fx_timestamp,in_stock,raw_price_text,source_url,source_type,page_fingerprint,collection_status,validation_status,validation_errors,sanity_outlier,sanity_reason,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(product_id,observation_date) DO UPDATE SET country=excluded.country,species_id=excluded.species_id,status=excluded.status,valid_until=excluded.valid_until,observed_at=excluded.observed_at,current_price=excluded.current_price,regular_price=excluded.regular_price,promotion_price=excluded.promotion_price,currency=excluded.currency,package_value=excluded.package_value,package_unit=excluded.package_unit,normalized_quantity_kg=excluded.normalized_quantity_kg,normalized_price_per_kg=excluded.normalized_price_per_kg,price_usd=excluded.price_usd,usd_rate_local_per_usd=excluded.usd_rate_local_per_usd,fx_source=excluded.fx_source,fx_timestamp=excluded.fx_timestamp,in_stock=excluded.in_stock,raw_price_text=excluded.raw_price_text,source_url=excluded.source_url,source_type=excluded.source_type,page_fingerprint=excluded.page_fingerprint,collection_status=excluded.collection_status,validation_status=excluded.validation_status,validation_errors=excluded.validation_errors,sanity_outlier=excluded.sanity_outlier,sanity_reason=excluded.sanity_reason").bind(`${x.platform}:${x.platform_product_id}:${x.observation_date}`,productId,x.country,x.species_id,x.status??"active",x.valid_until??null,new Date(x.observed_at).getTime(),x.observation_date,x.current_price,x.regular_price??null,x.promotion_price??null,x.currency,x.package_value??null,x.package_unit??null,x.normalized_quantity_kg??null,x.normalized_price_per_kg??null,x.price_usd??null,x.usd_rate_local_per_usd??null,x.fx_source??null,x.fx_timestamp??null,x.in_stock==null?null:Number(x.in_stock),x.raw_price_text??null,x.product_url,x.source_type,x.page_fingerprint??null,"collected",x.validation_status,JSON.stringify(x.review_reasons??[]),Number(Boolean(x.sanity_outlier)),x.sanity_reason??null,now)
   ];
   // species 字典表只收录已识别的物种（species.id 为主键，NULL 会违反 NOT NULL）；
   // 分类 unknown 的商品（species_id 为 null）跳过字典写入，products.species_id 列本身允许 null。
   if(x.species_id){stmts.unshift(db.prepare("INSERT INTO species(id,name_zh,name_en,dictionary_version,review_status) VALUES(?,?,?,?,?) ON CONFLICT(id) DO NOTHING").bind(x.species_id,x.species_id,x.species_id,"v1","seeded"));}
   await db.batch(stmts);written++;}catch(error){rejected++;errors.push({index,reason:error instanceof Error?error.message:"database write failed"});}
 }
 return Response.json({ok:true,written,updated:0,skipped,filtered,deleted,rejected,errors});
}

export async function DELETE(request:Request){
 if(!authorized(request))return Response.json({error:"Unauthorized"},{status:401});
 const body=await request.json().catch(()=>({})) as {id?:string;country?:string};
 if(!body.id&&!body.country)return Response.json({error:"id or country required"},{status:400});
 const db=(env as unknown as {DB:D1Database}).DB;
 const result=body.id?await db.prepare("DELETE FROM price_observations WHERE id=?").bind(body.id).run():await db.prepare("DELETE FROM price_observations WHERE country=?").bind(body.country).run();
 return Response.json({ok:true,deleted:result.meta.changes??0});
}
