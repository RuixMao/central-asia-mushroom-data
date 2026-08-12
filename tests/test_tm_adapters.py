"""土库曼斯坦（TM）适配器测试：gipertm + asmanexpress，离线 fixture"""
import pathlib, unittest
from unittest import mock

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pipeline"))

from adapters.gipertm import GiperAdapter
from adapters.asmanexpress import AsmanAdapter
from taxonomy import classify, normalize_price, parse_package

FIX = pathlib.Path(__file__).parent / "fixtures"


def _resp(html_path):
    r = mock.Mock()
    r.text = (FIX / html_path).read_text(encoding="utf-8", errors="ignore")
    return r


class TestGiperAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = GiperAdapter({"platform": "gipertm", "platform_name": "Giper.tm",
                                     "platform_product_id": "200763", "country": "TM", "city": "Ashgabat",
                                     "url": "https://gipertm.com/catalog/product/200763",
                                     "title": "Gelinkömelek (şampinýon) Tokaýçy 300 gr",
                                     "package": "300 g", "currency": "TMT", "language": "tk"})

    def test_parse_valid(self):
        row, err = self.adapter.parse(_resp("gip_mush_300.html"))
        self.assertIsNone(err)
        self.assertIn("şampinýon", row["original_title"])
        self.assertGreater(row["current_price"], 0)
        self.assertIn("TMT", row["raw_price_text"])
        self.assertEqual(row["currency"], "TMT")

    def test_missing_html(self):
        r = mock.Mock()
        r.text = "<html><body>no next data</body></html>"
        row, err = self.adapter.parse(r)
        self.assertIsNone(row)
        self.assertEqual(err, "next_data_missing")

    def test_zero_price_rejected(self):
        r = mock.Mock()
        r.text = '<script id="__NEXT_DATA__">{"props":{"pageProps":{"index":{"description":{"name":"X 300 gr"},"defaultAvailability":{"price":"0 TMT"}}}}}</script>'
        row, err = self.adapter.parse(r)
        self.assertIsNone(row)
        self.assertEqual(err, "zero_price")

    def test_classify_turkmen(self):
        # 土库曼语 şampinýon -> button_mushroom
        c = classify("Gelinkömelek (şampinýon) Tokaýçy 300 gr")
        self.assertEqual(c["species_id"], "button_mushroom")
        self.assertEqual(c["status"], "classified")

    def test_classify_marinad_pickled(self):
        c = classify("Esmo-marinadlanan bitin şampinýon kömelekleri 400 gr")
        self.assertEqual(c["species_id"], "button_mushroom")
        self.assertEqual(c["product_form"], "pickled")

    def test_parse_package_gr(self):
        p = parse_package("Gelinkömelek 300 gr")
        self.assertEqual(p["parse_status"], "valid")
        self.assertEqual(p["quantity_kg"], 0.3)


class TestAsmanAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = AsmanAdapter({"platform": "asmanexpress", "platform_name": "Asman Express",
                                     "platform_product_id": "44506", "country": "TM", "city": "Ashgabat",
                                     "url": "https://asmanexpress.com/mini/product/44506",
                                     "title": "Eyran komelek 1000 gr",
                                     "package": "1000 g", "currency": "TMT", "language": "tk"})

    def test_parse_valid(self):
        row, err = self.adapter.parse(_resp("asm_mush.html"))
        self.assertIsNone(err)
        self.assertIn("komelek", row["original_title"])
        self.assertEqual(row["current_price"], 68)
        self.assertIn("TMT", row["raw_price_text"])

    def test_missing_json(self):
        r = mock.Mock()
        r.text = "<html>no data</html>"
        row, err = self.adapter.parse(r)
        self.assertIsNone(row)
        self.assertEqual(err, "next_data_missing")

    def test_price_missing(self):
        r = mock.Mock()
        r.text = '<script id="__NEXT_DATA__">{"props":{"pageProps":{"product":{"name":"Eyran komelek"}}}}</script>'
        row, err = self.adapter.parse(r)
        self.assertIsNone(row)
        self.assertEqual(err, "price_missing")

    def test_classify_ambiguous_komelek(self):
        # 泛称 komelek -> unknown（诚实：不强行归为双孢菇）
        c = classify("Eyran komelek 1000 gr")
        self.assertIsNone(c["species_id"])
        self.assertEqual(c["status"], "unknown")

    def test_parse_package_1000gr(self):
        p = parse_package("Eyran komelek 1000 gr")
        self.assertEqual(p["parse_status"], "valid")
        self.assertEqual(p["quantity_kg"], 1.0)

    def test_normalize_price_per_kg(self):
        n = normalize_price(68, "1000 gr")
        self.assertEqual(n["price_per_kg"], 68.0)


if __name__ == "__main__":
    unittest.main()
