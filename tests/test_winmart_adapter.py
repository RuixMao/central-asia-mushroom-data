from adapters.winmart import WinMartAdapter


class FakeResponse:
    content = b"winmart"

    def raise_for_status(self):
        return None

    def json(self):
        return {"data": [
            {"sku": "shiitake", "description": "Nấm Đông Cô 200g", "seoName": "nam-dong-co-200g",
             "mch3Name": "Rau củ", "mch4Name": "Nấm", "mch5Name": "Nấm",
             "price": {"originPrice": 35000, "salePrice": 35000}, "warehouse": {"availableQuantity": 2}},
            {"sku": "sauce", "description": "Nước tương nấm 330ml", "seoName": "sauce",
             "mch3Name": "Thực phẩm khô", "mch4Name": "Gia vị", "mch5Name": "Nước tương",
             "price": {"salePrice": 19000}, "warehouse": {"availableQuantity": 5}},
            {"sku": "meatball", "description": "MEAT DELI Mọc viên nấm hương 250G", "seoName": "meatball",
             "mch3Name": "Thực phẩm tươi sống, Chế biến", "mch4Name": "Thực phẩm chế biến", "mch5Name": "",
             "price": {"salePrice": 66900}, "warehouse": {"availableQuantity": 5}},
        ]}


def test_winmart_public_api_filters_non_mushroom_products(monkeypatch):
    monkeypatch.setattr("adapters.winmart.requests.post", lambda *args, **kwargs: FakeResponse())
    rows, error = WinMartAdapter({"url": "https://winmart.vn/search/n%E1%BA%A5m", "query_term": "nấm"}).collect_many()
    assert error is None
    assert len(rows) == 1
    assert rows[0]["platform_product_id"] == "shiitake"
    assert rows[0]["current_price"] == 35000
    assert rows[0]["package"] == "Nấm Đông Cô 200g"
