"""Flagma 中亚站公开 B2B 列表适配器。面议记录只返回 gap，不伪造价格。

注意:Flagma 各站实际只索引俄语检索词——哈萨克语/乌兹别克语等本地语言词
会返回 404(如 flagma.kz/products/q=саңырауқұлақ/)。因此本适配器只应收到
俄语任务;调用方在构造 SOURCES 时应跳过本地语言词。
"""
import hashlib
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from utils import safe_get, find_price_match, response_text


MUSHROOM = re.compile(
    r"гриб|шампин|вешен|шиитак|"
    r"саңырауқұлақ|козу\s+карын|занбӯруғ|"
    r"qo['‘’`]ziqorin|shampinyon|sampinyon|veshenka|k[oö]melek|şampinýom",
    re.I,
)
# 菌丝/种子/培养包/设备等不是可食用菌商品,匹配即排除(与 taxonomy EXCLUDE_ONLY 一致)
NON_FOOD = re.compile(r"мицел|семен|спор|набор для выращ|грибной блок|субстрат|компост|увлажнитель|оборудован", re.I)
CULTIVATION_INPUT = re.compile(r"мицел|грибной блок|субстрат|компост|спор", re.I)
PRICE = re.compile(r"(\d[\d\s,.]{0,15})\s*(?:₸|KZT|сум|UZS|сом(?:они)?|KGS|TJS|TMT|c\.|с\.)", re.I)
NEGOTIABLE = re.compile(r"цена\s+(?:по\s+)?договор|договорная|уточняйте|по запросу", re.I)


class FlagmaAdapter:
    def __init__(self, config):
        self.config = config

    def collect_many(self):
        response = safe_get(self.config["url"], retries=2, backoff=3)
        if not response:
            return [], "unreachable"
        soup = BeautifulSoup(response_text(response), "html.parser")
        rows = {}
        saw_negotiable = False
        for anchor in soup.find_all("a", href=True):
            title = " ".join(anchor.get_text(" ", strip=True).split())
            cultivation_input = bool(CULTIVATION_INPUT.search(title))
            if not MUSHROOM.search(title) or (NON_FOOD.search(title) and not cultivation_input):
                continue
            scope = anchor.parent or anchor
            scope_text = " ".join(scope.get_text(" ", strip=True).split())
            if NEGOTIABLE.search(scope_text):
                saw_negotiable = True
                continue
            match, price = find_price_match(scope, PRICE)
            if not match:
                continue
            if not price or price <= 0:
                continue
            url = urljoin(response.url, anchor["href"])
            product_id = re.sub(r"\W+", "-", url.rstrip("/").split("/")[-1])[:120]
            rows[product_id] = {**self.config, "platform_product_id": product_id,
                "url": url, "original_title": title, "current_price": price,
                "b2b_category": "cultivation_input" if cultivation_input else "edible_mushroom",
                "seller": " ".join((scope.select_one('[class*=company],[class*=seller]') or anchor).get_text(" ", strip=True).split()),
                "raw_price_text": match.group(0), "source_type": "b2b_listing",
                "page_fingerprint": hashlib.sha256(response.content).hexdigest()}
        if rows:
            return list(rows.values()), None
        return [], "price_on_request" if saw_negotiable else "no_mushroom_products"
