import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/"pipeline"))
from adapters.kaspi import KaspiAdapter
ROOT=pathlib.Path(__file__).parent/"fixtures"
class KaspiTest(unittest.TestCase):
 def test_rendered_fixture(self):
  row,error=KaspiAdapter({"platform":"kaspi-kz","url":"https://kaspi.kz/shop/search/?text=шампиньон","package":"500 g"}).parse_rendered((ROOT/"kaspi_search_rendered.html").read_text(encoding="utf-8"))
  self.assertIsNone(error);self.assertEqual(row["current_price"],1590);self.assertIn("10001",row["url"])
 def test_missing_is_gap(self):
  row,error=KaspiAdapter({"url":"x"}).parse_rendered("<main>Нет товаров</main>")
  self.assertIsNone(row);self.assertEqual(error,"price_missing")
if __name__=="__main__":unittest.main()
