"""Wildberries 公开搜索接口适配器；限流或参数失效时返回明确 gap。"""
import hashlib
from urllib.parse import urlencode

from utils import safe_get


class WildberriesAdapter:
    ENDPOINT = "https://search.wb.ru/exactmatch/ru/common/v9/search"

    def __init__(self, config):
        self.config = config

    def collect_many(self):
        rows = {}
        for query in self.config.get("queries", ["шампиньоны", "вешенки", "шиитаке", "эноки"]):
            params = {"appType": 1, "curr": self.config["currency"].lower(),
                      "dest": self.config["dest"], "query": query,
                      "resultset": "catalog", "spp": 30}
            response = safe_get(f"{self.ENDPOINT}?{urlencode(params)}", retries=2, backoff=3)
            if not response:
                continue
            try:
                products = response.json().get("data", {}).get("products", [])
            except (ValueError, AttributeError):
                continue
            for item in products:
                product_id = str(item.get("id") or "")
                title = str(item.get("name") or "").strip()
                price_units = item.get("salePriceU") or item.get("priceU")
                if not product_id or not title or not isinstance(price_units, (int, float)) or price_units <= 0:
                    continue
                price = float(price_units) / 100
                rows[product_id] = {**self.config, "platform_product_id": product_id,
                    "url": f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx",
                    "original_title": title, "current_price": price,
                    "raw_price_text": str(price), "source_type": "json_api",
                    "page_fingerprint": hashlib.sha256(response.content).hexdigest()}
        return (list(rows.values()), None) if rows else ([], "rate_limited_or_no_products")
