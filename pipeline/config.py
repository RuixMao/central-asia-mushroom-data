import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv()
SITE_URL = os.environ.get("SITE_URL", "http://localhost").rstrip("/")
CRON_SECRET = os.environ.get("CRON_SECRET", "")
AI_PROVIDER = os.environ.get("AI_PROVIDER", "deepseek")
_AI_API_KEY_RAW = os.environ.get("AI_API_KEY", "")
_AI_API_KEY_MATCH = re.search(r"sk-[A-Za-z0-9_-]+", _AI_API_KEY_RAW)
AI_API_KEY = _AI_API_KEY_MATCH.group(0) if _AI_API_KEY_MATCH else _AI_API_KEY_RAW.strip()
AI_BASE_URL = os.environ.get("AI_BASE_URL", "https://api.deepseek.com")
AI_MODEL = os.environ.get("AI_MODEL", "deepseek-v4-flash")
UN_COMTRADE_API_KEY = os.environ.get("UN_COMTRADE_API_KEY", "")

SCOPE_PATH = Path(__file__).resolve().parents[1] / "scope.json"
SCOPE = json.loads(SCOPE_PATH.read_text(encoding="utf-8"))
COUNTRIES = {
    country["code"]: {
        "currency": country["currency"],
        "lang": country["languages"][0],
        "local_lang": country["languages"][0],
        "search_languages": country["languages"],
        "reporter": country["reporter"],
        "tier": country["tier"],
        "timezone": country["timezone"],
        "platforms": [(channel["id"], channel["url"]) for channel in country["channels"]],
    }
    for country in SCOPE["countries"]
}
TARGET_SPECIES = {
    species["slug"]: {"zh": species["name"], **species.get("terms", {})}
    for species in SCOPE["species"]
}
VARIETIES = {species["name"]: species.get("terms", {}) for species in SCOPE["species"]}
HS_CODES = ("070951", "070959", "200310")
