import os
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv()
SITE_URL = os.environ.get("SITE_URL", "http://localhost").rstrip("/")
CRON_SECRET = os.environ.get("CRON_SECRET", "")
AI_PROVIDER = os.environ.get("AI_PROVIDER", "deepseek")
AI_API_KEY = os.environ.get("AI_API_KEY", "")
AI_BASE_URL = os.environ.get("AI_BASE_URL", "https://api.deepseek.com")
AI_MODEL = os.environ.get("AI_MODEL", "deepseek-v4-flash")
UN_COMTRADE_API_KEY = os.environ.get("UN_COMTRADE_API_KEY", "")

COUNTRIES = {
 "KZ":{"currency":"KZT","lang":"ru","reporter":398,"platforms":[("arbuz","https://arbuz.kz/ru/almaty/search?query={q}"),("carefood","https://carefood.kz/search/?q={q}"),("flagma_kz","https://flagma.kz/ru/products/q={q}/")]},
 "UZ":{"currency":"UZS","lang":"uz","reporter":860,"platforms":[("uzum","https://uzum.uz/ru/search?query={q}"),("korzinka","https://korzinka.uz/catalog/?q={q}"),("makro","https://makromarket.uz/catalog"),("lochin","https://lochin.uz/search?q={q}"),("yukber","https://yukber.uz/uz/sabzovotlar"),("olx_uz","https://www.olx.uz/list/q-{q}/"),("tegen","https://tegen.uz/search?q={q}")]},
 "KG":{"currency":"KGS","lang":"ru","reporter":417,"platforms":[("globus","https://globus-online.kg/ru-kg/search?q={q}"),("omarket","https://market.o.kg/bishkek/search?q={q}"),("lalafo","https://lalafo.kg/kyrgyzstan/q-{q}")]},
 "TJ":{"currency":"TJS","lang":"ru","reporter":762,"platforms":[("zudbiyor","https://zudbiyor.tj/search?q={q}"),("magnit","https://magnit.tj/search?query={q}"),("somon","https://somon.tj/search/?q={q}")]},
 "TM":{"currency":"TMT","lang":"ru","reporter":795,"platforms":[("tm_market","https://www.goshmak.com/search?q={q}"),("flagma_tm","https://flagma-tm.com/ru/products/q={q}/")]},
}
VARIETIES={
 "双孢菇":{"ru":"шампиньон","uz":"qo'ziqorin","en":"white mushroom"},
 "平菇":{"ru":"вешенка","uz":"veshenka","en":"oyster mushroom"},
 "香菇":{"ru":"шиитаке","uz":"shiitake","en":"shiitake"},
 "金针菇":{"ru":"эноки","uz":"enoki","en":"enoki"},
 "木耳":{"ru":"древесный гриб","uz":"yog'och qo'ziqorini","en":"wood ear"},
}
TARGET_SPECIES={
 "button_mushroom":{"zh":"双孢菇","ru":"шампиньоны","en":"button mushroom"},
 "oyster_mushroom":{"zh":"平菇","ru":"вешенки","en":"oyster mushroom"},
 "shiitake":{"zh":"香菇","ru":"шиитаке","en":"shiitake"},
 "enoki":{"zh":"金针菇","ru":"эноки","en":"enoki"},
 "king_oyster_mushroom":{"zh":"杏鲍菇","ru":"эринги","en":"king oyster mushroom"},
}
HS_CODES=("070951","070959","200310")
FX_TO_CNY={"KZT":0.014,"UZS":0.00058,"KGS":0.083,"TJS":0.66,"TMT":2.04}
