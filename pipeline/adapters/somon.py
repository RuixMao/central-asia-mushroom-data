import re
from bs4 import BeautifulSoup
from .base import ProductAdapter

# Somon.tj：商品页标题价格形如 "Грибы шампиньоны 10 c."（10 сомони/кг）
SOMONI_PRICE = re.compile(r"(\d[\d\s]{1,12}(?:[.,]\d{1,2})?)\s*c\.", re.I)


class SomonAdapter(ProductAdapter):
    """Somon.tj 商品详情页解析（固定 URL 直抓）。

    Somon 广告页的价格通常内嵌在标题/og:title 中，格式为
    "Грибы шампиньоны 10 c."——数字后跟 "c." 表示 сомони（塔吉克索莫尼）。
    缺失时返回 price_missing，由调用方按 gap 处理，不写 0。
    """

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        og = soup.find("meta", property="og:title")
        title = (og.get("content") if og else None) or (soup.title.string if soup.title else "") or ""
        title = re.sub(r"\s+", " ", title).strip()
        if not title:
            return None, "title_missing"
        match = SOMONI_PRICE.search(title)
        if not match:
            return None, "price_missing"
        price = float(match.group(1).replace(" ", "").replace(",", "."))
        if price <= 0:
            return None, "zero_price"
        return {**self.config, "original_title": title, "current_price": price, "raw_price_text": match.group(0)}, None
