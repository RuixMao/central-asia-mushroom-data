import sys,unittest
sys.path.insert(0,"pipeline")
from taxonomy import classify,normalize_price,parse_package
class TaxonomyTest(unittest.TestCase):
 def test_species(self):
  cases={"Грибы Эноки 300 г":"enoki","Грибы Вешенки":"oyster_mushroom","Грибы шиитаке":"shiitake","Шампиньоны":"button_mushroom"}
  for title,want in cases.items():self.assertEqual(classify(title)["species_id"],want)
 def test_uncertain(self):
  self.assertEqual(classify("Грибы")["status"],"unknown")
  self.assertEqual(classify("Смесь шиитаке и вешенки")["status"],"mixed_species")
  self.assertEqual(classify("Шампиньоны",description="вешенка")["status"],"review_required")
 def test_forms(self):
  self.assertEqual(classify("Шампиньоны замороженные")["product_form"],"frozen")
  self.assertEqual(classify("Грибы сушеные Шиитаке")["product_form"],"dried")
  self.assertEqual(classify("Шампиньоны маринованные")["product_form"],"pickled")
  self.assertEqual(classify("Грибной соус")["status"],"excluded")
 def test_packages(self):
  self.assertEqual(parse_package("300 г")["normalized_quantity_kg"],.3)
  self.assertEqual(parse_package("250 g × 2")["normalized_quantity_kg"],.5)
  self.assertEqual(parse_package("2 × 250 g")["normalized_quantity_kg"],.5)
  self.assertIsNone(parse_package("1 pack")["normalized_quantity_kg"])
  self.assertEqual(normalize_price(120,"300 g")["price_per_kg"],400)
  self.assertEqual(normalize_price(120,"300 g",90)["price_per_kg"],300)
  with self.assertRaises(ValueError):normalize_price(0,"1 kg")
if __name__=="__main__":unittest.main()
