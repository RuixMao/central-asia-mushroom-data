import hashlib
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base import ProductAdapter
from utils import safe_get

# OLX 乌兹别克斯坦：商品页价格形如 "65 000 сум"（乌兹别克苏姆）
SUM_PRICE = re.compile(r"(\d[\d\s]{1,12}(?:[.,]\d{1,2})?)\s*сум\b", re.I)


class OlxAdapter(ProductAdapter):
    """OLX.uz 商品详情页解析（固定 URL 直抓）。

    价格优先取自 og:title（如 "Шампиньоны ...: 65 000 сум"），
    页面主体也可能包含相同价格文本。OLX 为 C2C 平台，B2B 整箱价
    居多，规格不确定时由归一化逻辑标记 needs_review，绝不伪造。
    """

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        og = soup.find("meta", property="og:title")
        title = (og.get("content") if og else None) or (soup.title.string if soup.title else "") or ""
        title = re.sub(r"\s+", " ", title).strip()
        if not title:
            return None, "title_missing"
        match = SUM_PRICE.search(title)
        if not match:
            return None, "price_missing"
        price = float(match.group(1).replace(" ", "").replace(",", "."))
        if price <= 0:
            return None, "zero_price"
        return {**self.config, "original_title": title, "current_price": price, "raw_price_text": match.group(0)}, None


class OlxSearchAdapter(ProductAdapter):
    """Parse OLX's public mobile search list instead of blocked detail pages."""

    EDIBLE = re.compile(r"(?:шампин|вешен|shiitake|shampinyon|qo[‘'`]ziqorin)", re.I)
    EXCLUDED = re.compile(
        r"(?:семен|уруг|уруғ|мицел|блок|капсул|чайн|молочн|комбуч|увлажнител|сушилк|книг)", re.I)

    def collect_many(self):
        response = safe_get(
            self.config["url"], retries=2, backoff=2,
            headers={"User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
                                   "AppleWebKit/537.36 Chrome/124 Mobile Safari/537.36"})
        if not response:
            return [], "unreachable"
        soup = BeautifulSoup(response.text, "html.parser")
        rows, seen = [], set()
        for anchor in soup.select('a[href*="/d/obyavlenie/"]'):
            href = urljoin(response.url, anchor.get("href", ""))
            title = " ".join(anchor.get_text(" ", strip=True).split())
            if not href or href in seen or not self.EDIBLE.search(title) or self.EXCLUDED.search(title):
                continue
            node, match = anchor, None
            for _ in range(3):
                node = node.parent
                if node is None:
                    break
                match = SUM_PRICE.search(" ".join(node.get_text(" ", strip=True).split()))
                if match:
                    break
            if not match:
                continue
            price = float(match.group(1).replace(" ", "").replace(",", "."))
            if price <= 0:
                continue
            product_match = re.search(r"-(ID[A-Za-z0-9]+)\.html", href)
            product_id = product_match.group(1) if product_match else hashlib.sha256(href.encode()).hexdigest()[:16]
            seen.add(href)
            rows.append({**self.config, "platform_product_id": product_id, "url": href,
                         "original_title": title, "current_price": price,
                         "raw_price_text": match.group(0), "source_type": "server_html"})
        if not rows:
            return [], "price_missing"
        fingerprint = hashlib.sha256(response.content).hexdigest()
        return [{**row, "page_fingerprint": fingerprint} for row in rows], None
