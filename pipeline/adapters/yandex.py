import hashlib
import re
from bs4 import BeautifulSoup
from .render import RenderedProductAdapter

# Yandex Market（乌兹别克斯坦站）：渲染后页面文本中价格形如 "50 000 сум"
SUM_PRICE = re.compile(r"(\d[\d\s]{2,12})\s*сум\b", re.I)
MUSHROOM = re.compile(r"шампиньон|вешенк|гриб", re.I)


class YandexMarketAdapter(RenderedProductAdapter):
    """Yandex Market UZ 商品搜索页解析（浏览器渲染后取 body 文本）。

    页面商品列表由 JS 异步加载，静态请求拿不到；渲染完成后商品标题与
    价格会出现在 body 文本中（如 "Шампиньоны свежие 500 г 50 000 сум"）。
    策略：在渲染后的纯文本里找【含菌词 + N сум】的片段，取第一个命中。
    若渲染被验证页拦截或未找到价格，返回错误码由调用方按 gap 处理。
    """

    def parse_rendered(self, html, body=""):
        rows = self.parse_rendered_many(html, body)
        if not rows:
            return None, "price_missing"
        return rows[0], None

    def parse_rendered_many(self, html, body=""):
        """返回渲染后页面所有【含菌词 + N сум】的商品片段。

        每条商品用序号后缀区分 platform_product_id（搜索页无独立商品链接），
        避免多条入库时因唯一键相同而互相覆盖。跳过 UI 文案行
        （如 "Каталог товаров Шампиньоны — купить..."）与已收录标题。空结果返回 []。
        """
        text = re.sub(r"\s+", " ", body or "")
        if not text:
            return []
        rows = []
        seen_titles = set()
        for m in MUSHROOM.finditer(text):
            seg = text[m.start():m.start() + 140]
            match = SUM_PRICE.search(seg)
            if not match:
                continue
            title = seg[: match.end()].strip()
            # 跳过 UI 文案/面包屑行（含促销用语，非商品卡片）
            if re.search(r"купить по низкой цене|Каталог товаров|Market Yandex|— купить|в корзину|скидк", title, re.I):
                continue
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)
            price = float(match.group(1).replace(" ", ""))
            if price <= 0:
                continue
            stable_title = re.sub(r"\W+", " ", title.lower(), flags=re.UNICODE).strip()
            pid = f"yandex-uz-{hashlib.sha256(stable_title.encode('utf-8')).hexdigest()[:16]}"
            rows.append({**self.config, "platform_product_id": pid, "url": self.config["url"],
                         "original_title": title[:240], "current_price": price,
                         "raw_price_text": match.group(0)})
        return rows
