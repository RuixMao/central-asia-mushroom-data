"""解析 Next.js 页面内嵌的商品结构化数据。"""

import hashlib
import json

from bs4 import BeautifulSoup

from adapters.catalog_search import MUSHROOM, NON_FOOD
from utils import safe_get, response_text


def _walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


class NextDataProductAdapter:
    def __init__(self, config):
        self.config = config

    def collect_many(self):
        response = safe_get(self.config["url"], retries=2, backoff=2)
        if not response:
            return [], "unreachable"
        return self.parse_html(response_text(response), response.content)

    def parse_html(self, html, content=None):
        soup = BeautifulSoup(html, "html.parser")
        script = soup.select_one("script#__NEXT_DATA__")
        if not script:
            return [], "next_data_missing"
        try:
            payload = json.loads(script.string or script.get_text())
        except (TypeError, ValueError):
            return [], "next_data_invalid"
        rows = {}
        for product in _walk(payload):
            title = str(product.get("name") or "").strip()
            if not title or not MUSHROOM.search(title) or NON_FOOD.search(title):
                continue
            price = product.get("finalPricePerUOW") or product.get("currentPrice") or product.get("price")
            try:
                price = float(price)
            except (TypeError, ValueError):
                continue
            if price <= 0:
                continue
            sku = str(product.get("sku") or product.get("id") or "").strip()
            if not sku:
                continue
            weight = product.get("weightPerPiece")
            package = f"{float(weight):g} kg" if weight else ""
            url_key = product.get("urlKey")
            product_url = f'{self.config["url"].split("/product/")[0]}/product/{url_key}' if url_key else self.config["url"]
            rows[sku] = {**self.config, "platform_product_id": sku, "url": product_url,
                         "original_title": title, "current_price": price, "package": package,
                         "package_verified": bool(weight), "in_stock": product.get("stockStatus") == "IN_STOCK",
                         "raw_price_text": str(price), "source_type": "next_data_structured",
                         "detail_verified": True,
                         "page_fingerprint": hashlib.sha256(content or html.encode("utf-8")).hexdigest()}
        return (list(rows.values()), None) if rows else ([], "no_mushroom_products")
