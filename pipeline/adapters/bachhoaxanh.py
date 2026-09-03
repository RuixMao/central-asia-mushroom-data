"""Bách Hóa XANH mushroom catalogue with API-to-storefront failover."""
import hashlib
import requests

from adapters.catalog_search import MUSHROOM, NON_FOOD, ProxyRenderedCatalogSearchAdapter
from utils import parse_price_text


class BachHoaXanhAdapter:
    API_URL = "https://api.bachhoaxanh.com/gw/Category/V2/GetCate"

    def __init__(self, config):
        self.config = config

    def _api_rows(self):
        params = {
            "provinceId": self.config.get("province_id", "1027"),
            "wardId": "0", "districtId": "0",
            "storeId": self.config.get("store_id", "2546"),
            "categoryUrl": self.config.get("category_slug", "nam-tuoi"),
            "isMobile": "true", "isV2": "true", "pageSize": "100", "page": "1",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 YinhengMarketResearch/1.0",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.bachhoaxanh.com",
            "Referer": self.config["url"], "referer-url": self.config["url"],
            "xapikey": "bhx-api-core-2022", "platform": "webnew",
        }
        try:
            response = requests.get(self.API_URL, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            products = ((response.json().get("data") or {}).get("products") or [])
        except (requests.RequestException, ValueError, AttributeError):
            return [], "unreachable"
        fingerprint = hashlib.sha256(response.content).hexdigest()
        rows = []
        for product in products:
            title = str(product.get("fullName") or product.get("name") or "").strip()
            if not MUSHROOM.search(title) or NON_FOOD.search(title):
                continue
            prices = product.get("productPrices") or []
            price_info = prices[0] if prices else {}
            price = parse_price_text(price_info.get("price") or price_info.get("sysPrice"))
            product_id = str(product.get("id") or "").strip()
            if not product_id or not price or price <= 0:
                continue
            product_url = product.get("url") or ""
            if product_url.startswith("/"):
                product_url = "https://www.bachhoaxanh.com" + product_url
            rows.append({**self.config, "platform_product_id": product_id,
                         "url": product_url or self.config["url"], "original_title": title,
                         "package": str(product.get("unit") or ""), "current_price": price,
                         "raw_price_text": str(price_info.get("price") or price_info.get("sysPrice")),
                         "source_type": "bachhoaxanh_api", "page_fingerprint": fingerprint,
                         "in_stock": True})
        return (rows, None) if rows else ([], "no_mushroom_products")

    def collect_many(self):
        rows, primary_error = self._api_rows()
        if rows:
            return rows, None
        rows, fallback_error = ProxyRenderedCatalogSearchAdapter(self.config).collect_many()
        if rows:
            for row in rows:
                row["source_type"] = "bachhoaxanh_storefront_fallback"
            return rows, None
        return [], f"primary:{primary_error};fallback:{fallback_error}"
