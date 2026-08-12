import re
from bs4 import BeautifulSoup
from .base import ProductAdapter

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
