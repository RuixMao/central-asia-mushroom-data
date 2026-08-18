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

def test_magnum_parses_product():
    html = """
    <html><body>
      <div class="product">
        <a href="/product/shampinony-1kg"><h3>Шампиньоны свежие 1 кг</h3></a>
        <span>1 890 ₸</span>
      </div>
    </body></html>
    """
    adapter = MagnumAdapter({"url": "https://magnum.kz/", "platform": "magnum-kz", "currency": "KZT"})
    rows = _rows(adapter, html)
    assert len(rows) == 1
    assert rows[0]["current_price"] == 1890
    assert rows[0]["platform_product_id"].startswith("magnum-")

def test_magnum_empty_page_honest_gap():
    adapter = MagnumAdapter({"url": "https://magnum.kz/", "platform": "magnum-kz", "currency": "KZT"})
    rows = _rows(adapter, "<html><body>Каталог скидок</body></html>")
    assert rows == []
