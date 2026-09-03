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
        # A second Vietnamese retailer prevents a BHX network policy or DNS
        # incident from turning the whole country into a zero-result day.
        alternatives = [
            ("WinMart", "https://winmart.vn/rau-cu-trai-cay--c02?storeCode=1539", "winmart_storefront_fallback"),
            ("BRG Shopping", "https://brgshopping.vn/rau-hoa-qua", "brg_storefront_fallback"),
            ("Siêu thị Thành Đô", "https://sieuthithanhdo.vn/nam-tuoi", "thanhdo_storefront_fallback"),
        ]
        alternative_errors = []
        for platform_name, url, source_type in alternatives:
            alternative_config = {**self.config, "platform_name": platform_name, "url": url, "title": "Nấm tươi"}
            rows, error = ProxyRenderedCatalogSearchAdapter(alternative_config).collect_many()
            if rows:
                for row in rows:
                    row["source_type"] = source_type
                return rows, None
            alternative_errors.append(f"{platform_name}:{error}")
        # Product-detail pages are substantially less dynamic than category
        # pages and remain usable when infinite-scroll catalogues change.
        detail_urls = [
            "https://brgshopping.vn/nong-san/nong-san/nam-huong-100g.html",
            "https://sieuthithanhdo.vn/nam-kim-cham-trang-long-hai-tui-150gr",
            "https://sieuthithanhdo.vn/nam-ngoc-cham-trang-gog-khay-200gr",
            "https://sieuthithanhdo.vn/nam-mo-gog-khay-200gr-1001562",
            "https://sieuthithanhdo.vn/nam-dui-ga-gog-huu-co-khay-250gr",
        ]
        detail_rows = {}
        for url in detail_urls:
            detail_config = {**self.config, "platform_name": "越南零售商", "url": url, "title": "Nấm"}
            rows, error = ProxyRenderedCatalogSearchAdapter(detail_config).collect_many()
            for row in rows:
                row["source_type"] = "vietnam_product_page_fallback"
                detail_rows[row["platform_product_id"]] = row
            if error:
                alternative_errors.append(f"detail:{error}")
        if detail_rows:
            return list(detail_rows.values()), None
        return [], f"primary:{primary_error};bhx_storefront:{fallback_error};" + ";".join(alternative_errors)
