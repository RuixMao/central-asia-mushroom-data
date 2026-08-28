"""FAOSTAT 蘑菇与松露产量：实时 API 优先，官方批量文件降级。"""
import csv,datetime as dt,io,json,os,zipfile
from pathlib import Path
from utils import log,post_to_site,safe_get

COUNTRIES={"KZ":108,"UZ":235,"KG":113,"TJ":208,"TM":213,"LA":120,"VN":237,"TH":216,"MM":28,"KH":115}
ITEM_CODE=449
ELEMENT_CODE=5510
API="https://fenixservices.fao.org/faostat/api/v1/en/data/QCL"
BULK="https://bulks-faostat.fao.org/production/Production_Crops_Livestock_E_All_Data_(Normalized).zip"

# FAOSTAT absence is a coverage gap, not evidence of zero production. These
# records preserve independently sourced local evidence without mixing reported
# output, planned capacity and export intentions into the official annual series.
LOCAL_EVIDENCE={
 "TJ":[
  {"record_type":"enterprise_output_reported","period":"spring season","value":1000.0,"unit":"kg","value_tonnes":1.0,"producer":"Valijon farm","verification_status":"reported_by_primary_institution","publication_date":"2025","source":"United Nations Tajikistan / WFP","source_url":"https://tajikistan.un.org/en/302680-mushroom-production-changed-lives","note":"单个农户春季采收量；不得外推为全国年产量"},
 ],
 "TM":[
  {"record_type":"enterprise_output_reported","period":"monthly","value":6.0,"unit":"t/month","producer":"Tiz hyzmat","verification_status":"reported_by_government","publication_date":"2022-08-08","source":"Government of Turkmenistan","source_url":"https://turkmenistan.gov.tm/ru/post/65371/shampinony-ot-tiz-hyzmat","note":"企业月产量报道；不得直接作为全国年产量"},
  {"record_type":"production_capacity_planned","period":"annual","value":600.0,"unit":"t/year","future_target_value":2500.0,"future_target_unit":"t/year","producer":"Ovadan-Depe mushroom project","verification_status":"government_reported_plan","publication_date":"2022-12-02","source":"Government of Turkmenistan","source_url":"https://turkmenistan.gov.tm/ru/post/68329/v-turkmenistane-sozdayutsya-krupnye-proizvodstva-po-promyshlennomu-vyrashchivaniyu-gribov","note":"计划产量及未来目标，不计入实际产量汇总"},
  {"record_type":"export_status","export_status":"planned","producer":"Altynnur zamany","verification_status":"government_reported_plan","source":"Government of Turkmenistan","source_url":"https://www.turkmenistan.gov.tm/en/post/89849/private-enterprise-altynnur-zamany-one-leaders-production-mushroom-products","note":"鲜菇和罐头出口为近期计划，尚非已验证出口"},
 ],
}

def _coverage_gap(reason,today):
 return {"status":"gap","reason":reason,"coverage_status":"not_reported_by_faostat" if reason=="no_records" else "source_unreachable","zero_production":False if reason=="no_records" else None,"display_label":"FAOSTAT 未收录；不代表产量为 0" if reason=="no_records" else "FAOSTAT 暂时无法访问","observed_at":today}

def _local_evidence(country,today):
 return [{"status":"evidence","country":country,"official_annual_total":False,"include_in_official_total":False,"observed_at":today,**record} for record in LOCAL_EVIDENCE.get(country,[])]

def _normalise(row):
 year=row.get("Year") or row.get("year");value=row.get("Value") if "Value" in row else row.get("value")
 if year is None or value in (None,""):return None
 flag=str(row.get("Flag") or row.get("flag") or "").strip();unit=str(row.get("Unit") or row.get("unit") or "t")
 estimated=flag.upper() in {"E","I"}
 return {"item":"Mushrooms and truffles","item_code":ITEM_CODE,"element":"Production","element_code":ELEMENT_CODE,"year":int(year),"value":float(value),"unit":unit,"value_tonnes":float(value),"flag":flag,"is_estimate":estimated,"estimate_label":"估算" if estimated else None,"flag_description":"插补估算" if flag.upper()=="I" else ("估算值" if flag.upper()=="E" else "官方值"),"source":"FAOSTAT"}

def _api_rows(area_code):
 response=safe_get(API,params={"area_code":area_code,"item_code":ITEM_CODE,"element_code":ELEMENT_CODE,"page_size":1000},retries=2,backoff=3,timeout=20)
 if not response:return None
 try:payload=response.json();records=payload.get("data") or payload.get("Data") or []
 except (ValueError,AttributeError):return None
 return [item for item in (_normalise(row) for row in records) if item]

def _bulk_rows():
 response=safe_get(BULK,retries=2,backoff=3,timeout=120)
 if not response:return None
 try:
  archive=zipfile.ZipFile(io.BytesIO(response.content));name=next(n for n in archive.namelist() if n.endswith("(Normalized).csv"));reader=csv.DictReader(io.TextIOWrapper(archive.open(name),encoding="utf-8-sig"))
  wanted=set(COUNTRIES.values());result={code:[] for code in COUNTRIES}
  reverse={value:code for code,value in COUNTRIES.items()}
  for row in reader:
   try:area=int(row["Area Code"]);item=int(row["Item Code"]);element=int(row["Element Code"])
   except (KeyError,TypeError,ValueError):continue
   if area not in wanted or item!=ITEM_CODE or element!=ELEMENT_CODE:continue
   parsed=_normalise(row)
   if parsed:result[reverse[area]].append(parsed)
  return result
 except (zipfile.BadZipFile,KeyError,StopIteration):return None

def run():
 dry=os.getenv("DRY_RUN","false").lower()=="true";wanted=os.getenv("COUNTRY","").strip().upper();countries=[wanted] if wanted in COUNTRIES else list(COUNTRIES)
 collected={};api_failed=[]
 for index,country in enumerate(countries):
  rows=_api_rows(COUNTRIES[country])
  if rows is None:
   # 域级 API 故障时不对其余国家重复等待超时，直接切官方批量文件。
   api_failed.extend(countries[index:]);break
  else:collected[country]=rows
 bulk=_bulk_rows() if api_failed else None
 for country in api_failed:collected[country]=(bulk or {}).get(country,[]) if bulk is not None else None
 output=[];today=dt.date.today().isoformat()
 for country in countries:
  rows=collected.get(country)
  if rows:
   for row in rows:
    data={"status":"live",**row,"source_url":API if country not in api_failed else BULK,"retrieval_method":"api" if country not in api_failed else "official_bulk","observed_at":today};output.append({"country":country,**data})
    if not dry:
     for data in [x for x in output if x["country"]==country]:post_to_site("/api/ingest/snapshot",{"metric":"production","country":country,"source":"FAOSTAT","data":{k:v for k,v in data.items() if k!="country"}})
  else:
   reason="api_and_bulk_unreachable" if rows is None else "no_records";gap=_coverage_gap(reason,today);output.append({"country":country,**gap})
   if not dry:post_to_site("/api/ingest/snapshot",{"metric":"production","country":country,"source":"FAOSTAT","data":gap})
   for evidence in _local_evidence(country,today):
    output.append(evidence)
    if not dry:post_to_site("/api/ingest/snapshot",{"metric":"production","country":country,"source":evidence["source"],"data":{k:v for k,v in evidence.items() if k!="country"}})
  log(f"FAOSTAT {country}: {len(rows or [])} 条")
 path=os.getenv("PRODUCTION_OUTPUT","").strip()
 if path:
  target=Path(path);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf-8");log(f"FAOSTAT 验证表已写入: {target}")
 return output

if __name__=="__main__":run()
