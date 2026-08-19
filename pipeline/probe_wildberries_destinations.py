"""按首都坐标探测 Wildberries buyer API 的真实配送 dest，不接受俄罗斯回落。"""
import json,os,re
from pathlib import Path
from adapters.wildberries import DESTINATIONS,GEO_ENDPOINT
from utils import log,safe_get

TARGETS={
 "KZ":(43.238949,76.889709,"KZT","kz"),"UZ":(41.299496,69.240073,"UZS","uz"),
 "KG":(42.874621,74.569762,"KGS","kg"),"TJ":(38.559772,68.787038,"TJS","tj"),
 "TM":(37.960077,58.326063,"TMT","tm"),
}
def run():
 output=[]
 for country,(lat,lon,currency,locale) in TARGETS.items():
  response=safe_get(GEO_ENDPOINT,params={"latitude":lat,"longitude":lon,"currency":currency},retries=2,backoff=3)
  if not response:output.append({"country":country,"status":"gap","reason":"geo_api_unreachable"});continue
  try:data=response.json()
  except (ValueError,AttributeError):output.append({"country":country,"status":"gap","reason":"geo_invalid_response"});continue
  match=re.search(r"(?:^|&)dest=([^&]+)",str(data.get("xinfo") or ""));dest=match.group(1) if match else None;actual_locale=data.get("locale");expected=DESTINATIONS.get(country)
  verified=bool(expected and dest==expected["dest"] and actual_locale==locale and str(data.get("currency") or "").upper()==currency)
  output.append({"country":country,"status":"live" if verified else "gap","dest":dest,"locale":actual_locale,"currency":data.get("currency"),"address":data.get("address"),"verified":verified,"reason":None if verified else "destination_country_mismatch"})
  log(f"WB dest {country}: {dest}/{actual_locale}, verified={verified}")
 path=os.getenv("WB_DEST_OUTPUT","").strip()
 if path:target=Path(path);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf-8")
 return output
if __name__=="__main__":run()
