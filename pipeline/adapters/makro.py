import hashlib
import re

from utils import safe_get


MUSHROOM = re.compile(r"(?:шампин|вешен|шиитак|shiitake|shampinyon|qo[‘'`]ziqorin)", re.I)
NON_RETAIL_MUSHROOM = re.compile(r"(?:пюре|pyure|суп|соус|flavou?r|ta'mli|urug|mitsel|micel|blok)", re.I)


class MakroAdapter:
    """Makro's public JSON product-list API.

    The API is stable even though the website search route currently returns
    a 404.  We scan the small current catalogue and emit only actual mushroom
    products, never flavour-only prepared foods.
    """

    API = "https://api.makromarket.uz/api/v2/product-list/?p=1&limit=500&offset=0"

    def __init__(self, config):
        self.config = config

    def collect_many(self):
        response = safe_get(self.API, retries=2, backoff=2)
        if not response:
            return [], "unreachable"
        try:
            payload = response.json()
            products = payload.get("results", [])
        except (ValueError, AttributeError):
            return [], "invalid_json"
        rows = []
        for item in products:
            title = str(item.get("title") or "").strip()
            price = item.get("newPrice")
            if not MUSHROOM.search(title) or NON_RETAIL_MUSHROOM.search(title):
                continue
            if not isinstance(price, (int, float)) or price <= 0:
                continue
            product_id = str(item.get("id") or item.get("code") or "").strip()
            if not product_id:
                continue
            rows.append({**self.config,
                         "platform_product_id": product_id,
                         "url": f"https://makromarket.uz/product/{product_id}",
                         "original_title": title,
                         "current_price": float(price),
                         "raw_price_text": f"{price:g} UZS",
                         "source_type": "json_api",
                         "page_fingerprint": hashlib.sha256(response.content).hexdigest()})
        if not rows:
            return [], "no_mushroom_products"
        return rows, None
