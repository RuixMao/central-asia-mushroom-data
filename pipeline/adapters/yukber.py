import re

from bs4 import BeautifulSoup

from .base import ProductAdapter


UZS_PRICE = re.compile(r"(\d[\d\s,.]{1,15})\s*UZS\b", re.I)


class YukberAdapter(ProductAdapter):
    """Yukber grocery product page adapter for server-rendered products."""

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        heading = soup.find("h1")
        title = heading.get_text(" ", strip=True) if heading else (soup.title.get_text(" ", strip=True) if soup.title else "")
        title = re.sub(r"\s+", " ", title).strip()
        if not title:
            return None, "title_missing"
        text = " ".join(soup.get_text(" ", strip=True).split())
        matches = [m for m in UZS_PRICE.finditer(text)
                   if float(m.group(1).replace(" ", "").replace(",", "")) > 0]
        if not matches:
            return None, "price_missing"
        # The first positive amount is the product price; later amounts belong
        # to the recommendations carousel.
        match = matches[0]
        price = float(match.group(1).replace(" ", "").replace(",", ""))
        return {**self.config, "original_title": title, "description": text[:2000],
                "current_price": price, "raw_price_text": match.group(0)}, None
