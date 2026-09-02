"""Foodpanda 商超公开 GraphQL 商品目录适配器。"""
import hashlib
import json
import time

import requests

from adapters.catalog_search import MUSHROOM, NON_FOOD
from utils import parse_price_text


PERSISTED_QUERY_HASH = "9ac98aae4b8e1eb9ae93f6213d71b06a1d557e948d3c2e7b15479221a0e913ad"


class FoodpandaGraphQLAdapter:
    endpoint = "https://la.fd-api.com/graphql"

    def __init__(self, config):
        self.config = config

    def _payload(self):
        return {
            "operationName": "GetGroceryCategoryDetailsPage",
            "variables": {
                "input": {
                    "vendorCode": self.config["vendor_code"],
                    "globalEntityID": self.config.get("global_entity_id", "FP_LA"),
                    "locale": self.config.get("locale", "en_LA"),
                    "isDarkstore": False,
                    "categoryID": self.config["category_id"],
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
        headers = {
            "User-Agent": "Mozilla/5.0 YinhengMarketResearch/1.0",
            "Origin": "https://www.foodpanda.la",
            "Referer": self.config["url"],
            "Accept": "application/json",
        }
        response = None
        for attempt in range(3):
            try:
                response = requests.post(self.endpoint, json=self._payload(), headers=headers, timeout=30)
                response.raise_for_status()
                break
            except requests.RequestException:
                response = None
                if attempt < 2:
                    time.sleep(2 ** attempt)
        if response is None:
            return [], "unreachable"
        try:
            payload = response.json()
            components = payload["data"]["groceryCategoryDetailsPage"]["components"]["listingComponents"]
        except (KeyError, TypeError, ValueError):
            return [], "invalid_catalog_response"

        fingerprint = hashlib.sha256(response.content).hexdigest()
        rows = {}
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
        return (parsed, None) if parsed else ([], "no_mushroom_products")
