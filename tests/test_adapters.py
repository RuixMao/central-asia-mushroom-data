import pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/"pipeline"))

from adapters.base import ProductAdapter
from adapters.arbuz import ArbuzAdapter
ROOT=pathlib.Path(__file__).parent/"fixtures"

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

def test_globus_fixture(monkeypatch):
    row,error=collect(monkeypatch,(ROOT/"globus.html").read_text(encoding="utf-8"))
    assert error is None and row["current_price"]==260

def test_omarket_fixture(monkeypatch):
    row,error=collect(monkeypatch,(ROOT/"omarket.html").read_text(encoding="utf-8"))
    assert error is None and row["current_price"]==128.70

def test_arbuz_json_fixture():
    import json
    class JsonResponse(Response):
        headers={"content-type":"application/json"}
        def json(self):return json.loads(self.text)
    adapter=ArbuzAdapter({"platform":"arbuz"})
    row=adapter.parse(JsonResponse((ROOT/"arbuz.json").read_text(encoding="utf-8")))
    assert row["current_price"]==1290 and row["regular_price"]==1490
