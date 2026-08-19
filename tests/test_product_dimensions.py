import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/"pipeline"))
from product_dimensions import describe_product

class ProductDimensionsTest(unittest.TestCase):
 def test_sliced_frozen_packaged(self):
  d=describe_product("Белый гриб резаный замороженный 300 г","frozen",300,"g")
  self.assertEqual((d["product_shape"],d["processing_state"],d["packaging_type"]),("sliced","frozen","packaged"))
 def test_bulk_weight_product(self):
  d=describe_product("Грибы шампиньоны, вес","fresh",1,"kg")
  self.assertEqual(d["packaging_type"],"bulk")
 def test_canned_whole_product(self):
  d=describe_product("RITA Bütewi Şampion kömelekler 400 gr","canned",400,"g")
  self.assertEqual(d["product_shape"],"whole")

if __name__=="__main__":unittest.main()
