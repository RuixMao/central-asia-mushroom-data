import re

from bs4 import BeautifulSoup

from .base import ProductAdapter


SUM_PRICE = re.compile(r"(\d[\d\s,.]{1,15})\s*сум\b", re.I)


class LochinAdapter(ProductAdapter):
    """Lochin supermarket product page adapter.

    Lochin exposes the product name and current UZS price in server-rendered
    HTML.  Weighted fresh products are configured as 1 kg because Lochin's
    ``вес`` catalogue unit is the kilogram; packaged products keep the
    explicit size from their title/configuration.
    """

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        title = re.sub(r"\s+-\s+Lochin\s*$", "", title, flags=re.I).strip()
        if not title:
            return None, "title_missing"

        text = " ".join(soup.get_text(" ", strip=True).split())
        marker = self.config.get("marker", title)
        start = text.lower().find(marker.lower())
        scoped = text[start:start + 500] if start >= 0 else text
        prices = [m for m in SUM_PRICE.finditer(scoped)
                  if float(m.group(1).replace(" ", "").replace(",", "")) > 0]
        if not prices:
            return None, "price_missing"
        match = prices[0]
        price = float(match.group(1).replace(" ", "").replace(",", ""))
        return {**self.config, "original_title": title,
                "current_price": price, "raw_price_text": match.group(0)}, None
