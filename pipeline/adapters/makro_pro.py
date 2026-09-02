"""Makro Pro 泰国/缅甸目录适配器。"""
import hashlib
import json
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from adapters.catalog_search import MUSHROOM, NON_FOOD
from utils import parse_price_text, response_text, safe_get


class MakroProAdapter:
    """读取页面内嵌的 Next.js 商品目录，避免依赖脆弱的页面卡片选择器。"""

    def __init__(self, config):
        self.config = config

    def collect_many(self):
        response = safe_get(self.config["url"], retries=2, backoff=2)
        if not response:
            return [], "unreachable"
        return self.parse_html(response_text(response), response.url, response.content)

    def parse_html(self, html, response_url, response_content=None):
        soup = BeautifulSoup(html, "html.parser")
        script = soup.select_one("script#__NEXT_DATA__")
        if not script:
            return [], "next_data_missing"
        try:
            payload = json.loads(script.string or script.get_text())
            hits = payload["props"]["pageProps"]["initialSearchResult"]["hits"]
        except (KeyError, TypeError, ValueError):
            return [], "invalid_next_data"

        fingerprint = hashlib.sha256(
            response_content if response_content is not None else html.encode("utf-8")
        ).hexdigest()
        rows = {}
        for hit in hits if isinstance(hits, list) else []:
            item = hit.get("document", hit) if isinstance(hit, dict) else {}
            if not isinstance(item, dict):
                continue
            search_title = item.get("searchTitle") or {}
            title = str(
                (search_title.get("EN") if isinstance(search_title, dict) else "")
                or item.get("titleEn")
                or item.get("title")
                or ""
            ).strip()
            if not MUSHROOM.search(title) or NON_FOOD.search(title):
                continue
            price = parse_price_text(item.get("displayPrice"))
            if not price or price <= 0:
                continue
            product_id = str(item.get("productId") or item.get("id") or item.get("makroId") or "").strip()
            if not product_id:
                continue
            makro_id = str(item.get("makroId") or "").strip()
            product_path = f"/en/p/{makro_id}-{product_id}" if makro_id else f"/en/p/{product_id}"
            row = {
                **self.config,
                "platform_product_id": product_id,
                "url": urljoin(response_url, product_path),
                "original_title": title,
                "current_price": price,
                "raw_price_text": str(item.get("displayPrice")),
                "source_type": "embedded_catalog_json",
                "page_fingerprint": fingerprint,
                "in_stock": bool(item.get("inStock", True)),
            }
            original_price = parse_price_text(item.get("originalPrice"))
            if original_price and original_price > 0:
                row["original_price"] = original_price
            rows[product_id] = row
        parsed = list(rows.values())
        return (parsed, None) if parsed else ([], "no_mushroom_products")
