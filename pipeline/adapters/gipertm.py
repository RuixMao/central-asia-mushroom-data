import json, re
from .base import ProductAdapter

# gipertm.com（土库曼斯坦）：Next.js 商品详情页
# 商品数据内嵌于 <script id="__NEXT_DATA__"> JSON：
#   props.pageProps.index.description.name            -> 商品名（如 "Gelinkömelek (şampinýon) "Tokaýçy" 300 gr"）
#   props.pageProps.index.defaultAvailability.price   -> "29 TMT"（字符串，带货币单位）
NEXT_DATA_RE = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)
TMT_PRICE = re.compile(r"([\d][\d\s.,]*)", re.I)


class GiperAdapter(ProductAdapter):
    """Giper 网店（TM）商品详情页解析。

    纯 HTTP 直抓，价格来自 __NEXT_DATA__ 内嵌 JSON。缺失/解析失败
    返回对应错误码，由调用方按 gap 处理，不写 0。
    """

    def parse(self, response):
        m = NEXT_DATA_RE.search(response.text)
        if not m:
            return None, "next_data_missing"
        try:
            data = json.loads(m.group(1))
        except (ValueError, json.JSONDecodeError):
            return None, "json_parse_error"
        idx = (data.get("props", {}).get("pageProps", {}).get("index", {})) or {}
        name = (idx.get("description") or {}).get("name") or ""
        avail = idx.get("defaultAvailability") or {}
        price_text = avail.get("price") or ""
        name = re.sub(r"\s+", " ", name).strip()
        if not name:
            return None, "title_missing"
        if not price_text:
            return None, "price_missing"
        pm = TMT_PRICE.search(price_text)
        if not pm:
            return None, "price_missing"
        price = float(pm.group(1).replace(" ", "").replace(",", "."))
        if price <= 0:
            return None, "zero_price"
        return {**self.config, "original_title": name, "current_price": price, "raw_price_text": price_text}, None
