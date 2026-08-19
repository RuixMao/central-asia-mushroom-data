import re

from bs4 import BeautifulSoup

from .base import ProductAdapter
from utils import find_price_match, response_text


SUM_PRICE = re.compile(r"(\d[\d\s,.]{1,15})\s*сум\b", re.I)


class LochinAdapter(ProductAdapter):
    """Lochin supermarket product page adapter.

    Lochin exposes the product name and current UZS price in server-rendered
    HTML. ``вес``只表示称重销售；页面未明确计价单位时不得默认按1kg换算。
    """

    def parse(self, response):
        soup = BeautifulSoup(response_text(response), "html.parser")
        heading = soup.find("h1")
        title = heading.get_text(" ", strip=True) if heading else (soup.title.get_text(" ", strip=True) if soup.title else "")
        title = re.sub(r"\s+-\s+Lochin\s*$", "", title, flags=re.I).strip()
        if not title:
            return None, "title_missing"

        text = " ".join(soup.get_text(" ", strip=True).split())
        marker = self.config.get("marker", title)
        start = text.lower().find(marker.lower())
        scoped = text[start:start + 500] if start >= 0 else text
        match, price = find_price_match(soup, SUM_PRICE)
        if not match:
            return None, "price_missing"
        return {**self.config, "original_title": title, "description": scoped,
                "current_price": price, "raw_price_text": match.group(0)}, None
