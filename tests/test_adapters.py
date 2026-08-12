import pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/"pipeline"))

from adapters.base import ProductAdapter

class Response:
    def __init__(self,text):
        self.text=text
        self.content=text.encode()

def collect(monkeypatch,html):
    monkeypatch.setattr("adapters.base.safe_get",lambda *args,**kwargs:Response(html))
    return ProductAdapter({"url":"https://public.example/product","title":"Шампиньоны"}).collect()

def test_latin_c_price(monkeypatch):
    row,error=collect(monkeypatch,"<main>Шампиньоны 128,70 c</main>")
    assert error is None and row["current_price"]==128.70

def test_skips_zero_cart_badge(monkeypatch):
    row,error=collect(monkeypatch,"<header>Корзина 0 сом</header><main>Шампиньоны 29.90 сом</main>")
    assert error is None and row["current_price"]==29.90
