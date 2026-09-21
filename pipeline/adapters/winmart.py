"""WinMart Vietnam public search API adapter."""

import hashlib
import re

import requests

from adapters.catalog_search import MUSHROOM, NON_FOOD
from utils import parse_price_text


class WinMartAdapter:
    API_URL = "https://api-crownx.winmart.vn/ss/api/v2/public/winmart/item-search"
    PREPARED_FOOD = re.compile(
        r"mọc viên|mushroom ball|yogurt|sữa chua|nước tương|hạt nêm|"
        r"mì |bánh |dầu hào|pork|chicken|gia vị|nước chấm",
        re.I,
    )

    def __init__(self, config):
        self.config = config

    def collect_many(self):
        payload = {
            "keyword": self.config.get("query_term", "nấm"),
            "pageNumber": 1,
            "storeNo": self.config.get("store_no", "1535"),
            "storeGroupCode": self.config.get("store_group_code", "1998"),
            "pageSize": self.config.get("page_size", 60),
            "applicationType": "Winmart",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 YinhengMarketResearch/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://winmart.vn",
            "Referer": "https://winmart.vn/",
            "x-api-merchant": "WCM",
        }
        try:
            response = requests.post(self.API_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            products = response.json().get("data") or []
        except (requests.RequestException, ValueError, AttributeError):
            return [], "unreachable"

        fingerprint = hashlib.sha256(response.content).hexdigest()
        rows = {}
        for product in products:
            title = str(product.get("description") or product.get("longDescription") or "").strip()
            category = " ".join(str(product.get(key) or "") for key in ("mch3Name", "mch4Name", "mch5Name"))
            # Vietnamese search is accent-sensitive but also returns words such as
            # "Nam Dương". Require the mushroom taxonomy/category in addition to
            # the title match, and reject sauces, noodles and prepared foods.
            if not MUSHROOM.search(title) or NON_FOOD.search(title):
                continue
            if self.PREPARED_FOOD.search(title):
                continue
            if "Nấm" not in category and "nấm" not in title.lower():
                continue
            if any(term in category.lower() for term in ("mì ăn liền", "gia vị", "nước tương", "thực phẩm chế biến đông lạnh")):
                continue
            price_info = product.get("price") or {}
            price = parse_price_text(price_info.get("salePrice") or price_info.get("originPrice"))
            product_id = str(product.get("sku") or product.get("itemNo") or product.get("id") or "").strip()
            if not product_id or not price or price <= 0:
                continue
            seo_name = str(product.get("seoName") or "").strip()
            product_url = f"https://winmart.vn/products/{seo_name}" if seo_name else self.config["url"]
            rows[product_id] = {
                **self.config,
                "platform_product_id": product_id,
                "url": product_url,
                "original_title": title,
                "package": title,
                "current_price": price,
                "regular_price": parse_price_text(price_info.get("originPrice")),
                "raw_price_text": str(price),
                "source_type": "winmart_public_api",
                "page_fingerprint": fingerprint,
                "in_stock": float((product.get("warehouse") or {}).get("availableQuantity") or 0) > 0,
                "detail_verified": True,
            }
        return (list(rows.values()), None) if rows else ([], "no_mushroom_products")
