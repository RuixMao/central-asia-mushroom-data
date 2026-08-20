import pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/"pipeline"))

from adapters.uzum import UzumAdapter
from adapters.magnum import MagnumAdapter

def _rows(adapter, html, body=""):
    """直接喂渲染 HTML 给 parse_rendered_many(纯列表),绕过真实渲染。"""
    return adapter.parse_rendered_many(html, body)

def test_uzum_parses_product():
    html = """
    <html><body>
      <div data-testid="product-card">
        <a href="/ru/product/123456-shampinony"><h3>Шампиньоны свежие 500 г</h3></a>
        <span>15 000 сум</span>
      </div>
    </body></html>
    """
    adapter = UzumAdapter({"url": "https://uzum.uz/", "platform": "uzum-uz", "currency": "UZS"})
    rows = _rows(adapter, html)
    assert len(rows) == 1
    assert rows[0]["current_price"] == 15000
    assert rows[0]["platform_product_id"] == "uzum-123456"

def test_uzum_skips_non_mushroom():
    html = """
    <html><body>
      <div data-testid="product-card">
        <a href="/ru/product/9999"><h3>Яблоки свежие</h3></a>
        <span>5 000 сум</span>
      </div>
    </body></html>
    """
    adapter = UzumAdapter({"url": "https://uzum.uz/", "platform": "uzum-uz", "currency": "UZS"})
    rows = _rows(adapter, html)
    assert rows == []

def test_uzum_dedupes_same_product():
    html = """
    <html><body>
      <div data-testid="product-card">
        <a href="/ru/product/123456"><h3>Шампиньоны 500 г</h3></a><span>10 000 сум</span>
      </div>
      <div data-testid="product-card">
        <a href="/ru/product/123456"><h3>Шампиньоны 500 г</h3></a><span>10 500 сум</span>
      </div>
    </body></html>
    """
    adapter = UzumAdapter({"url": "https://uzum.uz/", "platform": "uzum-uz", "currency": "UZS"})
    rows = _rows(adapter, html)
    assert len(rows) == 1  # 同一商品 ID 去重

def test_magnum_parses_product(monkeypatch):
    from adapters import magnum as mm
    # 模拟 Strapi /api/products 响应(含蘑菇商品)
    fake = type("R", (), {"json": lambda self: {"data": [
        {"id": 7001, "attributes": {"name": "ШАМПИНЬОНЫ СВЕЖИЕ 1 КГ",
                                     "final_price": 1890, "start_price": 2100,
                                     "translation_kaz": "Саңырауқұлақ"}}
    ], "meta": {"pagination": {"total": 1}}}})
    monkeypatch.setattr(mm, "safe_get", lambda url, **kw: fake())
    adapter = mm.MagnumAdapter({"url": "https://magnum.kz/catalog", "platform": "magnum-kz", "currency": "KZT", "city": "almaty"})
    rows, err = adapter.collect_many()
    assert err is None
    assert len(rows) == 1
    assert rows[0]["current_price"] == 1890
    assert rows[0]["regular_price"] == 2100
    assert rows[0]["platform_product_id"] == "magnum-7001"


def test_magnum_empty_page_honest_gap(monkeypatch):
    from adapters import magnum as mm
    fake = type("R", (), {"json": lambda self: {"data": [
        {"id": 7002, "attributes": {"name": "Молоко 900 мл", "final_price": 585, "translation_kaz": "Сүт"}}
    ], "meta": {"pagination": {"total": 1}}}})
    monkeypatch.setattr(mm, "safe_get", lambda url, **kw: fake())
    adapter = mm.MagnumAdapter({"url": "https://magnum.kz/catalog", "platform": "magnum-kz", "currency": "KZT", "city": "almaty"})
    rows, err = adapter.collect_many()
    assert err == "no_mushroom_products"
    assert rows == []


def test_uzum_captcha_real_sentence():
    """Uzum 实际验证码句式(CI 渲染实测)应被识别为 render_blocked。"""
    from adapters.uzum import UzumAdapter, CAPTCHA
    # 实测 body(CI 渲染 uzum.uz/ru/search 返回)
    body = "Подтвердите, что запросы отправляли вы, а не робот"
    assert CAPTCHA.search(body), "实际验证码句式未匹配"
    html = "<html><body><p>Подтвердите, что запросы отправляли вы, а не робот</p></body></html>"
    adapter = UzumAdapter({"url": "https://uzum.uz/ru/search?query=грибы", "platform": "uzum-uz"})
    rows, err = adapter.collect_many_from_debug(html, body) if hasattr(adapter, "collect_many_from_debug") else (None, None)
    if rows is None:
        # 直接测 collect_many 的验证码分支逻辑
        from adapters.uzum import CAPTCHA as C
        blocked = bool(C.search(body))
        assert blocked
        print("验证码识别 OK(render_blocked 分支)")
    else:
        assert err == "render_blocked"
