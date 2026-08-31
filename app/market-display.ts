import { southeastAsiaCodes, speciesScope, targetMarketCodes, targetMarketNames } from "./market-scope";

export type LivePriceRow={observation_date:string;observed_at?:string|number;created_at?:string|number;country:string;country_name?:string;city?:string;species_id:string;species_name?:string;product_form?:string;original_title?:string;platform_name:string;current_price:number|null;regular_price?:number|null;currency:string;package_value?:number|null;package_unit:string|null;normalized_quantity_kg?:number|null;normalized_usd_per_kg:number|null;price_usd_per_package?:number|null;usd_rate_local_per_usd?:number|null;fx_source?:string|null;fx_timestamp?:string|null;validation_status?:string;raw_price_text?:string;grade?:string;price_type?:string|null;price_notes?:string|null;source_url?:string;source_type?:string;status?:"active"|"archived"|"deleted";valid_until?:string|null;is_current?:boolean};

export const countryNames = targetMarketNames;
export const seaCodes = [...southeastAsiaCodes];
export const allCodes = [...targetMarketCodes];
export const marketCodesFromRows=(rows:Pick<LivePriceRow,"country">[])=>Array.from(new Set([...allCodes,...rows.map(row=>row.country)]));
export const marketName=(row:Pick<LivePriceRow,"country"|"country_name">)=>row.country_name||countryNames[row.country]||row.country;
export const speciesMeta:Record<string,{zh:string;en:string;priority:number}>=Object.fromEntries(speciesScope.map(item=>[item.slug,{zh:item.name,en:item.terms.en,priority:item.priority}]));
export const speciesLabel=(id:string,withEnglish=false)=>{const item=speciesMeta[id];if(!item)return "其他食用菌";return withEnglish?`${item.zh} ${item.en}`:item.zh};
export const customerPlatformName=(name:string)=>name.replace(/（老挝锚）|\(老挝锚\)/g,"").replace(/供给锚/g,"市场参考").replace(/邻国锚/g,"周边市场价格").trim();
export const speciesPriority=(id:string)=>speciesMeta[id]?.priority??99;
export const rowPrice=(row:LivePriceRow)=>{
  const local=row.raw_price_text??`${new Intl.NumberFormat("zh-CN",{maximumFractionDigits:2}).format(Number(row.current_price??0))} ${row.currency}${row.package_unit?`/${row.package_unit}`:""}`;
  const isRange=row.regular_price!=null&&row.current_price!=null&&row.regular_price>row.current_price;
  if(row.currency==="USD")return local;
  const usd=isRange&&row.normalized_usd_per_kg!=null
    ?`US$${Number(row.normalized_usd_per_kg).toFixed(2)}–${(Number(row.normalized_usd_per_kg)*(Number(row.regular_price)/Number(row.current_price))).toFixed(2)}/kg`
    :row.price_usd_per_package!=null
    ?`US$${Number(row.price_usd_per_package).toFixed(2)}/包装`
    :row.current_price!=null&&row.usd_rate_local_per_usd
      ?`US$${(row.current_price/row.usd_rate_local_per_usd).toFixed(2)}/包装`
      :row.normalized_usd_per_kg!=null
        ?`US$${Number(row.normalized_usd_per_kg).toFixed(2)}/kg`
        :null;
  return usd?`${local}（约 ${usd}）`:local;
};
export const speciesIdFromProduct=(product:string)=>speciesScope.find(item=>product.includes(item.name))?.slug??"other";
const liveDataEndpoint="https://api.yinheng.site/api/powerbi?table=prices";
export const loadLivePrices=()=>fetch(liveDataEndpoint,{cache:"no-store"}).then(async response=>{if(!response.ok)throw new Error("price load failed");const payload=await response.json() as {records?:LivePriceRow[]};return (payload.records??[]).map(row=>({...row,platform_name:customerPlatformName(row.platform_name)}));});
export const observationDateRank=(value:string)=>{const exact=value.match(/^(\d{4})-(\d{2})-(\d{2})$/);if(exact)return Number(`${exact[1]}${exact[2]}${exact[3]}`);const years=value.match(/(?:19|20)\d{2}/g)?.map(Number)??[];return years.length?Math.max(...years)*10000:0};
export const latestByCountry=(rows:LivePriceRow[])=>{const latest=new Map<string,number>();rows.forEach(row=>{const rank=observationDateRank(row.observation_date);if(rank>(latest.get(row.country)??0))latest.set(row.country,rank)});return rows.filter(row=>observationDateRank(row.observation_date)===latest.get(row.country));};
export const prioritizedRows=(rows:LivePriceRow[],limit=10)=>[...rows].sort((a,b)=>speciesPriority(a.species_id)-speciesPriority(b.species_id)||b.observation_date.localeCompare(a.observation_date)||Number(b.normalized_usd_per_kg??0)-Number(a.normalized_usd_per_kg??0)).filter((row,index,all)=>{const peers=all.slice(0,index).filter(item=>item.country===row.country&&item.species_id===row.species_id);return peers.length<2}).slice(0,limit);

export type PriceCategory="retail"|"dining"|"wholesale"|"historical"|"neighbor";
export const priceCategory=(row:LivePriceRow):PriceCategory=>{
  const type=`${row.price_type??""} ${row.product_form??""} ${row.price_notes??""}`;
  if(row.grade==="E"||/邻国/.test(type))return "neighbor";
  if(row.grade==="D"||/历史/.test(type))return "historical";
  if(/prepared|餐饮|菜品|单串|plate/i.test(type))return "dining";
  if(/批发|到岸|出厂|wholesale|FOB|CIF|进口/.test(type))return "wholesale";
  return "retail";
};
export const priceCategoryLabels:Record<PriceCategory,string>={retail:"零售商品",dining:"餐饮菜品",wholesale:"批发到岸",historical:"历史基准",neighbor:"邻国参考"};
export const activePriceRows=(rows:LivePriceRow[])=>rows.filter(row=>(row.status??"active")==="active");
export const latestWriteDate=(rows:LivePriceRow[])=>{
  const value=Math.max(0,...activePriceRows(rows).map(row=>{const raw=row.created_at??row.observed_at??0;return typeof raw==="number"?raw:Date.parse(raw)}).filter(Number.isFinite));
  return value?new Intl.DateTimeFormat("en-CA",{timeZone:"Asia/Singapore",year:"numeric",month:"2-digit",day:"2-digit"}).format(new Date(value)):"";
};
const gradeRank=(grade?:string)=>({A:0,B:1,C:2,D:3,E:4}[grade??""]??5);
const commercialRank=(row:LivePriceRow)=>/出厂/.test(row.price_type??"")?0:priceCategory(row)==="retail"&&/干|dried/i.test(row.product_form??row.original_title??"")?1:priceCategory(row)==="retail"?2:priceCategory(row)==="wholesale"?3:4;
export const representativeRows=(rows:LivePriceRow[],limit=12)=>activePriceRows(rows).filter(row=>row.is_current!==false&&["A","B","C","D"].includes(row.grade??"")&&priceCategory(row)!=="dining").sort((a,b)=>(a.country===seaCodes[0]?-1:0)-(b.country===seaCodes[0]?-1:0)||commercialRank(a)-commercialRank(b)||speciesPriority(a.species_id)-speciesPriority(b.species_id)||gradeRank(a.grade)-gradeRank(b.grade)||observationDateRank(b.observation_date)-observationDateRank(a.observation_date)).filter((row,index,all)=>all.slice(0,index).every(item=>item.country!==row.country||item.species_id!==row.species_id)).slice(0,limit);
export const getMarketSummary=(rows:LivePriceRow[])=>{
  const active=activePriceRows(rows),current=active.filter(row=>row.is_current!==false),retailComparable=current.filter(row=>priceCategory(row)==="retail");
  return {rows:active,current,retailComparable,countryCount:new Set(active.map(row=>row.country)).size,channelCount:new Set(active.map(row=>`${row.country}|${row.platform_name}`)).size,speciesCount:new Set(active.map(row=>row.species_id).filter(Boolean)).size,updated:latestWriteDate(active),representatives:representativeRows(active,20)};
};
