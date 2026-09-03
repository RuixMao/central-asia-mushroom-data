"""Foodpanda 商超公开 GraphQL 商品目录适配器。"""
import hashlib
import json
import re
import time

import requests

from adapters.catalog_search import MUSHROOM, NON_FOOD
from utils import parse_price_text


PERSISTED_QUERY_HASH = "9ac98aae4b8e1eb9ae93f6213d71b06a1d557e948d3c2e7b15479221a0e913ad"


class FoodpandaGraphQLAdapter:
    def __init__(self, config):
        self.config = config

    @property
    def endpoint(self):
        return self.config.get("api_endpoint") or "https://la.fd-api.com/graphql"

    def _category_ids(self):
        configured = self.config.get("category_ids") or ([self.config["category_id"]] if self.config.get("category_id") else [])
        if configured:
            return list(dict.fromkeys(configured))
        # Foodpanda storefront HTML exposes category deep links. Discovering them
        # keeps the collector independent of short-lived category UUID changes.
        try:
            response = requests.get(self.config["url"], headers={"User-Agent": "Mozilla/5.0 YinhengMarketResearch/1.0"}, timeout=30)
            response.raise_for_status()
            ids = re.findall(r"(?:category/|categoryID(?:%22|\"|')?[:=](?:%22|\"|'))([0-9a-f-]{36})", response.text, re.I)
            return list(dict.fromkeys(ids))
        except requests.RequestException:
            return []

    def _payload(self, category_id):
        return {
            "operationName": "GetGroceryCategoryDetailsPage",
            "variables": {
                "input": {
                    "vendorCode": self.config["vendor_code"],
                    "globalEntityID": self.config.get("global_entity_id", "FP_LA"),
                    "locale": self.config.get("locale", "en_LA"),
                    "isDarkstore": False,
                    "categoryID": category_id,
                    "platform": "web",
                    "funWithFlags": [{"name": "pd-qc-weight-stepper", "value": "Variation1"}],
                },
                "sort": "RECOMMENDED",
                "filters": {"filterOnSale": False},
            },
            "extensions": {
                "clientLibrary": {"name": "@apollo/client", "version": "4.0.12"},
                "persistedQuery": {"version": 1, "sha256Hash": PERSISTED_QUERY_HASH},
            },
        }

    def collect_many(self):
        category_ids = self._category_ids()
        if not category_ids:
            return [], "category_discovery_failed"
        origin = self.config.get("origin") or self.config["url"].split("/en/shop/")[0]
        headers = {
            "User-Agent": "Mozilla/5.0 YinhengMarketResearch/1.0",
            "Origin": origin,
            "Referer": self.config["url"],
            "Accept": "application/json",
        }
        rows = {}
        failures = []
        for category_id in category_ids:
            response = None
            for attempt in range(3):
                try:
                    response = requests.post(self.endpoint, json=self._payload(category_id), headers=headers, timeout=30)
                    response.raise_for_status()
                    break
                except requests.RequestException:
                    response = None
                    if attempt < 2:
                        time.sleep(2 ** attempt)
            if response is None:
                failures.append("unreachable")
                continue
            try:
                payload = response.json()
                components = payload["data"]["groceryCategoryDetailsPage"]["components"]["listingComponents"]
            except (KeyError, TypeError, ValueError):
                failures.append("invalid_catalog_response")
                continue
            fingerprint = hashlib.sha256(response.content).hexdigest()
            for component in components if isinstance(components, list) else []:
                for item in (component.get("items") or []) if isinstance(component, dict) else []:
                    title = str(item.get("name") or "").strip()
                    if not MUSHROOM.search(title) or NON_FOOD.search(title):
                        continue
                    price = parse_price_text(item.get("price"))
                    product_id = str(item.get("id") or item.get("globalCatalogID") or "").strip()
                    if not product_id or not price or price <= 0:
                        continue
                    weight = ((item.get("attributes") or {}).get("contentsWeightInfo") or {})
                    unit = str(weight.get("unit") or "").upper()
                    value = weight.get("value")
                    package = ""
                    if value not in (None, 0, ""):
                        package = f"{value} g" if unit == "GRAM" else f"{value} kg" if unit == "KILOGRAM" else f"{value} packet" if unit == "PACKETS" else ""
                    rows[product_id] = {
                        **self.config,
                        "platform_product_id": product_id,
                        "url": self.config["url"],
                        "original_title": title,
                        "package": package,
                        "package_verified": unit in {"GRAM", "KILOGRAM"} and value not in (None, 0, ""),
                        "current_price": price,
                        "raw_price_text": str(item.get("price")),
                        "source_type": "foodpanda_graphql_catalog",
                        "page_fingerprint": fingerprint,
                        "in_stock": bool(item.get("isAvailable", True)),
                    }
        parsed = list(rows.values())
        return (parsed, None) if parsed else ([], failures[0] if failures else "no_mushroom_products")


class FoodpandaPrimaryFallbackAdapter:
    """Use the public catalog API first, then the storefront HTML/browser."""

    def __init__(self, config):
        self.config = config

    def collect_many(self):
        rows, primary_error = FoodpandaGraphQLAdapter(self.config).collect_many()
        if rows:
            return rows, None
        from adapters.catalog_search import ProxyRenderedCatalogSearchAdapter
        rows, fallback_error = ProxyRenderedCatalogSearchAdapter(self.config).collect_many()
        if rows:
            for row in rows:
                row["source_type"] = "foodpanda_storefront_fallback"
            return rows, None
        return [], f"primary:{primary_error};fallback:{fallback_error}"
