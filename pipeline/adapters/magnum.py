"""Magnum.kz(哈萨克连锁商超)适配器。

Magnum 是 Nuxt SPA:静态页只有导航,商品列表由前端异步加载,
本地无法直接定位其数据 API(常见路径已探测 404)。
策略:渲染型框架,渲染成功但无商品 → no_mushroom_products(诚实 gap);
待 CI 环境逆向 API 后补充 JSON 通道。不做猜测抓取。
"""
import hashlib
import re

from bs4 import BeautifulSoup

from .render import RenderedProductAdapter

KZT_PRICE = re.compile(r"(\d[\d\s,.]{1,15})\s*(?:₸|тг|тенге)", re.I)


class MagnumAdapter(RenderedProductAdapter):
    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def collect_many(self):
        rendered, error = self.render(self.config["url"])
        if error:
            return [], error
        html, body = rendered
        rows = self.parse_rendered_many(html, body)
        if not rows:
            return [], "no_mushroom_products"
        return rows, None

    def parse_rendered_many(self, html, body=""):
        soup = BeautifulSoup(html, "html.parser")
        rows = {}
        for card in soup.select('[data-testid="product-card"], .product-card, .catalog-item, .product'):
            text = " ".join(card.get_text(" ", strip=True).split())
            if not re.search(r"гриб|шампин|вешен|шиитак|эноки|эринги", text, re.I):
                continue
            match = KZT_PRICE.search(text)
            if not match:
                continue
            price = float(match.group(1).replace(" ", "").replace(",", ""))
            if price <= 0:
                continue
            link = card.find("a", href=True)
            url = link["href"] if link else self.config["url"]
            if url.startswith("/"):
                url = "https://magnum.kz" + url
            product_id = re.sub(r"\W+", "-", url.rstrip("/").split("/")[-1])[:60] or hashlib.sha256(url.encode()).hexdigest()[:16]
            rows[product_id] = {**self.config, "platform_product_id": f"magnum-{product_id}",
                                "url": url, "original_title": text[:240],
                                "current_price": price, "raw_price_text": match.group(0),
                                "source_type": "rendered",
                                "page_fingerprint": hashlib.sha256(html.encode()).hexdigest()}
        return list(rows.values())
