"""City Mall Myanmar server-rendered catalogue adapter."""

import hashlib
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from adapters.catalog_search import MUSHROOM, NON_FOOD
from utils import parse_price_text, response_text, safe_get


class CityMallAdapter:
    PREPARED_FOOD = re.compile(
        r"yogurt|ball|pork|chicken|meat|sausage|noodle|soup|seasoning|sauce|"
        r"ဝက်သား|ကြက်သား",
        re.I,
    )

    def __init__(self, config):
        self.config = config

    def collect_many(self):
        response = safe_get(self.config["url"], retries=2, backoff=2)
        if not response:
            return [], "unreachable"
        soup = BeautifulSoup(response_text(response), "html.parser")
        fingerprint = hashlib.sha256(response.content).hexdigest()
        rows = {}
        for card in soup.select(".product-listing"):
            title_node = card.select_one(".product-title a.name")
            price_node = card.select_one(".product-price")
            package_node = card.select_one(".product-packaging")
            if not title_node or not price_node:
                continue
            title = " ".join(title_node.get_text(" ", strip=True).split())
            if not MUSHROOM.search(title) or NON_FOOD.search(title) or self.PREPARED_FOOD.search(title):
                continue
            price = parse_price_text(re.sub(r"[^0-9,.]", "", price_node.get_text(" ", strip=True)))
            href = title_node.get("href") or ""
            product_id_match = re.search(r"/p/([^/]+)", href)
            product_id = product_id_match.group(1) if product_id_match else href.rstrip("/").split("/")[-1]
            if not product_id or not price or price <= 0:
                continue
            product_url = urljoin(response.url, href)
            detail = safe_get(product_url, retries=1, backoff=1)
            detail_text = response_text(detail) if detail else ""
            detail_verified = bool(detail and title.casefold() in detail_text.casefold() and str(int(price)) in detail_text.replace(",", ""))
            rows[product_id] = {
                **self.config,
                "platform_product_id": product_id,
                "url": product_url,
                "original_title": title,
                "package": (package_node.get_text(" ", strip=True) if package_node else title),
                "package_verified": bool(package_node),
                "current_price": price,
                "raw_price_text": price_node.get_text(" ", strip=True),
                "source_type": "citymall_catalog_detail",
                "page_fingerprint": fingerprint,
                "in_stock": True,
                "detail_verified": detail_verified,
            }
        return (list(rows.values()), None) if rows else ([], "no_mushroom_products")
