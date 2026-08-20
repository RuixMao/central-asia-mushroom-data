import json, re
from .base import ProductAdapter
from utils import response_text

# asmanexpress.com（土库曼斯坦）：Next.js 商品详情页
# 商品数据内嵌于 <script id="__NEXT_DATA__"> JSON：
#   props.pageProps.product.name   -> 商品名（如 "Eyran komelek 1000 gr"）
#   props.pageProps.product.price  -> 68（数字，单位 TMT）
NEXT_DATA_RE = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)


class AsmanAdapter(ProductAdapter):
    """Asman Express 网店（TM）商品详情页解析。

    纯 HTTP 直抓，价格来自 __NEXT_DATA__ 内嵌 JSON（数字，货币 TMT）。
    缺失/解析失败返回对应错误码，由调用方按 gap 处理，不写 0。
    """

    def parse(self, response):
        m = NEXT_DATA_RE.search(response_text(response))
        if not m:
            return None, "next_data_missing"
        try:
            data = json.loads(m.group(1))
        except (ValueError, json.JSONDecodeError):
            return None, "json_parse_error"
        prod = (data.get("props", {}).get("pageProps", {}).get("product", {})) or {}
        name = (prod.get("name") or "").strip()
        price = prod.get("price")
        name = re.sub(r"\s+", " ", name).strip()
        if not name:
            return None, "title_missing"
        if price is None:
            return None, "price_missing"
        price = float(price)
        if price <= 0:
            return None, "zero_price"
        return {**self.config, "original_title": name, "current_price": price, "raw_price_text": f"{price:g} TMT"}, None
