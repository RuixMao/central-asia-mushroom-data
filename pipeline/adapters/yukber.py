import re

from bs4 import BeautifulSoup

from .base import ProductAdapter
from utils import find_price_match, response_text


UZS_PRICE = re.compile(r"(\d[\d\s,.]{1,15})\s*UZS\b", re.I)


class YukberAdapter(ProductAdapter):
    """Yukber grocery product page adapter for server-rendered products."""

    def parse(self, response):
        soup = BeautifulSoup(response_text(response), "html.parser")
        heading = soup.find("h1")
        title = heading.get_text(" ", strip=True) if heading else (soup.title.get_text(" ", strip=True) if soup.title else "")
        title = re.sub(r"\s+", " ", title).strip()
        if not title:
            return None, "title_missing"
        text = " ".join(soup.get_text(" ", strip=True).split())
        match, price = find_price_match(soup, UZS_PRICE)
        if not match:
            return None, "price_missing"
        # The first positive amount is the product price; later amounts belong
        # to the recommendations carousel.
        return {**self.config, "original_title": title, "description": text[:2000],
                "current_price": price, "raw_price_text": match.group(0)}, None
