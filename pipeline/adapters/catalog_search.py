"""面向公开搜索页的通用多商品适配器。"""
import hashlib
import json
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from utils import safe_get


MUSHROOM = re.compile(r"гриб|шампин|вешен|шиитак|эноки|qo['’`]ziqorin|shampinyon|k[oö]melek", re.I)
NON_FOOD = re.compile(r"мицел|семен|спор|набор для выращ|грибной блок|urug|mitsel", re.I)
PRICE = re.compile(r"(\d[\d\s,.]{0,15})\s*(?:₸|KZT|сом|KGS|сум|UZS|TJS|TMT)", re.I)


def _walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


class CatalogSearchAdapter:
    """优先解析 JSON-LD；再从包含菌类关键词的商品链接附近提取价格。"""

    def __init__(self, config):
        self.config = config

    def collect_many(self):
        response = safe_get(self.config["url"], retries=2, backoff=2)
        if not response:
            return [], "unreachable"
        soup = BeautifulSoup(response.text, "html.parser")
        rows = {}
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                payload = json.loads(script.string or script.get_text())
            except (TypeError, ValueError):
                continue
            for item in _walk(payload):
                kind = item.get("@type")
                if kind not in ("Product", ["Product"]):
                    continue
                title = str(item.get("name") or "").strip()
                if not MUSHROOM.search(title) or NON_FOOD.search(title):
                    continue
                offers = item.get("offers") or {}
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                price = offers.get("price") or offers.get("lowPrice")
                try:
                    price = float(str(price).replace(" ", "").replace(",", "."))
                except (TypeError, ValueError):
                    continue
                if price <= 0:
                    continue
                url = urljoin(response.url, str(item.get("url") or offers.get("url") or ""))
                product_id = str(item.get("sku") or item.get("productID") or url.rstrip("/").split("/")[-1])
                if not product_id:
                    continue
                rows[product_id] = self._row(product_id, title, price, url, response)

        if not rows:
            for anchor in soup.find_all("a", href=True):
                title = " ".join(anchor.get_text(" ", strip=True).split())
                if not MUSHROOM.search(title) or NON_FOOD.search(title):
                    continue
                scope = anchor.parent.get_text(" ", strip=True) if anchor.parent else title
                match = PRICE.search(scope)
                if not match:
                    continue
                price = float(match.group(1).replace(" ", "").replace(",", "."))
                if price <= 0:
                    continue
                url = urljoin(response.url, anchor["href"])
                product_id = re.sub(r"\W+", "-", url.rstrip("/").split("/")[-1])[:120]
                rows[product_id] = self._row(product_id, title, price, url, response)
        return (list(rows.values()), None) if rows else ([], "no_mushroom_products")

    def _row(self, product_id, title, price, url, response):
        return {**self.config, "platform_product_id": product_id, "url": url,
                "original_title": title, "current_price": price,
                "raw_price_text": str(price), "source_type": "search_page",
                "page_fingerprint": hashlib.sha256(response.content).hexdigest()}
