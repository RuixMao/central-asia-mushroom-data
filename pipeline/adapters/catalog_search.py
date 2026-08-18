"""面向公开搜索页的通用多商品适配器。"""
import hashlib
import json
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from utils import safe_get


MUSHROOM = re.compile(
    r"гриб|шампин|вешен|шиитак|эноки|"
    r"саңырауқұлақ|коз(?:у)?\s+кар|опята|занбӯруғ|"
    r"qo['‘’`]ziqorin|shampinyon|sampinyon|veshenka|k[oö]melek|şampinýom",
    re.I,
)
# 排除非可食用菌:菌丝/种子/培养包/设备/教材/书籍/科普等
NON_FOOD = re.compile(
    r"мицел|семен|спор|набор для выращ|грибной блок|urug|mitsel|"
    r"учебник|класс|биолог|книг|реферат|презентац|"
    r"субстрат|компост|увлажнитель|оборудован",
    re.I,
)
PRICE = re.compile(r"(\d[\d\s,.]{0,15})\s*(?:₸|KZT|сом|KGS|сум|UZS|TJS|TMT|c\.|с\.)", re.I)


def _parse_price(raw):
    """千分位/小数点兼容解析:45,000 -> 45000;1,234.56 -> 1234.56;128,70 -> 128.70"""
    s = raw.replace(" ", "").replace("\u202f", "").strip()
    if not s:
        return None
    if "," in s and "." in s:
        s = s.replace(",", "")
    elif "," in s:
        parts = s.split(",")
        if len(parts) >= 3 or (len(parts) == 2 and len(parts[1]) == 3 and len(parts[0]) > 0):
            s = s.replace(",", "")
        else:
            s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


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
        # 部分中亚站点没有正确的 HTTP charset，requests 会把 UTF-8
        # 页面误解为 ISO-8859-1，从而让本地语言商品名变成乱码。
        try:
            html = response.content.decode("utf-8")
        except UnicodeDecodeError:
            html = response.text
        soup = BeautifulSoup(html, "html.parser")
        rows = {}
        # React 目录页通常把商品卡片直接内嵌在 HTML 中，标题和价格并不在同一个链接里。
        for card in soup.select('[data-testid="product-card"]'):
            title_node = card.find("h3")
            title = " ".join((title_node or card).get_text(" ", strip=True).split())
            if not MUSHROOM.search(title) or NON_FOOD.search(title):
                continue
            match = PRICE.search(" ".join(card.get_text(" ", strip=True).split()))
            link = card.find("a", href=True)
            if not match or not link:
                continue
            price = _parse_price(match.group(1))
            url = urljoin(response.url, link["href"])
            product_id = url.rstrip("/").split("/")[-1]
            if product_id and price > 0:
                rows[product_id] = self._row(product_id, title, price, url, response)
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
                price = _parse_price(match.group(1))
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
