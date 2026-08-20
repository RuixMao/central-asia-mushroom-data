"""Magnum.kz(哈萨克连锁商超)适配器 —— 直连 Strapi JSON API。

逆向结论(2026-08-18,Playwright 拦截网络请求实测):
  - 后端是 Strapi(magnum.kz:1337/api/),商品数据走公开 JSON API
  - 全量商品:/api/products?pagination[page]=N&pagination[pageSize]=100
    (Almaty 共 1558 件,Strapi 标准 data[].attributes 结构)
  - 商品字段:name(标题)、start_price(原价)、final_price(现价)、
    discount(折扣率)、translation_kaz(哈萨克语名)
  - 促销新品:/api/new-product(city 参数)
  - 分类:/api/new-product-catalog(16 个分类)

数据事实:Almaty 当前全量目录与促销商品中**暂无蘑菇**上架(实测 1548 件无
蘑菇词)。适配器逻辑已就绪,一旦有蘑菇商品会自动产出,不虚构数据。

相比渲染型,JSON API 直连更快(毫秒级)、更稳(无浏览器依赖、无 SPA 异步加载)。
"""
import hashlib
import re

from utils import safe_get

API_BASE = "https://magnum.kz:1337"
PAGE_SIZE = 100
MUSHROOM = re.compile(
    r"гриб|шампин|вешен|шиитак|эноки|эринги|"
    r"саңырауқұлақ|коз(?:у)?\s+кар|опята|занбӯруғ|"
    r"qo['‘’`]ziqorin|shampinyon|sampinyon|veshenka|k[oö]melek|şampinýom",
    re.I,
)
NON_FOOD = re.compile(
    r"мицел|семен|спор|набор для выращ|грибной блок|urug|mitsel|"
    r"соус|приправ|вкус|аромат",
    re.I,
)


class MagnumAdapter:
    """直连 Strapi /api/products 拉全量商品,过滤蘑菇。"""

    def __init__(self, config):
        self.config = config

    def collect_many(self):
        city = self.config.get("city", "almaty").lower()
        rows = {}
        # 分页拉全量(上限 30 页,1558 件约 16 页)
        for page in range(1, 31):
            url = f"{API_BASE}/api/products?pagination[page]={page}&pagination[pageSize]={PAGE_SIZE}"
            r = safe_get(url, retries=2, backoff=2)
            if not r:
                return list(rows.values()), ("unreachable" if not rows else None)
            try:
                data = r.json().get("data", [])
            except ValueError:
                return list(rows.values()), ("unreachable" if not rows else None)
            for item in data:
                attr = item.get("attributes", {})
                name = str(attr.get("name") or "")
                kaz = str(attr.get("translation_kaz") or "")
                title = name or kaz
                if not MUSHROOM.search(name) and not MUSHROOM.search(kaz):
                    continue
                if NON_FOOD.search(name) or NON_FOOD.search(kaz):
                    continue
                final = attr.get("final_price")
                start = attr.get("start_price")
                if final is None or float(final) <= 0:
                    continue
                pid = f"magnum-{item.get('id')}"
                rows[pid] = {**self.config,
                             "platform_product_id": pid,
                             "url": f"https://magnum.kz/products/{item.get('id')}?city={city}",
                             "original_title": title[:240],
                             "current_price": float(final),
                             "regular_price": float(start) if start else None,
                             "promotion_price": float(start) if start else None,
                             "raw_price_text": (f"{float(start):.0f}->{float(final):.0f}" if start else f"{float(final):.0f}"),
                             "source_type": "json_api",
                             "page_fingerprint": hashlib.sha256(url.encode()).hexdigest()}
            if len(data) < PAGE_SIZE:
                break
        if rows:
            return list(rows.values()), None
        return [], "no_mushroom_products"
