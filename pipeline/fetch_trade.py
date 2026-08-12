import datetime as dt
import time
from config import COUNTRIES, HS_CODES, UN_COMTRADE_API_KEY
from utils import log, post_to_site, safe_get

def run():
    years = (dt.date.today().year - 1, dt.date.today().year)
    for country, cfg in COUNTRIES.items():
        for hs in HS_CODES:
            for year in years:
                url = f"https://comtradeapi.un.org/data/v1/get/C/A/HS?period={year}&reporterCode={cfg['reporter']}&flowCode=M&partnerCode=0&cmdCode={hs}&partner2Code=0&customsCode=C00&motCode=0&maxRecords=50"
                headers = {"Ocp-Apim-Subscription-Key": UN_COMTRADE_API_KEY} if UN_COMTRADE_API_KEY else {}
                response = safe_get(url, headers=headers)
                rows = response.json().get("data", []) if response else []
                if not rows: log(f"trade gap {country} {hs} {year}"); time.sleep(1.5); continue
                row = rows[0]
                post_to_site("/api/ingest/snapshot", {"metric":"trade","country":country,"source":"UN Comtrade","data":{"hs":hs,"year":year,"value_usd":row.get("primaryValue"),"net_weight_kg":row.get("netWgt"),"status":"live"}})
                time.sleep(1.5)
if __name__ == "__main__": run()
