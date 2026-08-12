import sys,unittest
sys.path.insert(0,"pipeline")
from taxonomy import classify,normalize_price
class TaxonomyTest(unittest.TestCase):
 def test_species(self):
  self.assertEqual(classify("Грибы Эноки 300 г")["species_id"],"flammulina_velutipes")
  self.assertEqual(classify("Грибы Вешенки 300 г")["species_id"],"pleurotus_ostreatus")
  self.assertEqual(classify("Грибы Шиитаке 100 г")["species_id"],"lentinula_edodes")
 def test_mixed_unknown_excluded(self):
  self.assertEqual(classify("Mixed oyster and shiitake mushrooms 300 g")["status"],"mixed_species")
  self.assertEqual(classify("Грибы")["status"],"unknown")
  self.assertEqual(classify("Грибы Эноки в фирменном соусе")["status"],"excluded")
 def test_package(self):
  self.assertEqual(normalize_price(120,"300 g")["price_per_kg"],400)
  self.assertIsNone(normalize_price(120,"1 pack")["price_per_kg"])
if __name__=="__main__":unittest.main()
