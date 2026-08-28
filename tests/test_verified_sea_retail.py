import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))
from publish_verified_sea_retail import ROWS

class VerifiedSeaRetailTest(unittest.TestCase):
    def test_all_rows_have_comparable_fields_and_unique_products(self):
        self.assertGreaterEqual(len(ROWS), 30)
        self.assertEqual(len(ROWS), len({(r[2], r[4]) for r in ROWS}))
        self.assertTrue(all(r[6] in {"fresh", "dried", "frozen", "pickled"} for r in ROWS))
        self.assertTrue(all(r[7] > 0 and r[8] > 0 and r[9] in {"THB", "VND", "USD"} and r[10].startswith("https://") for r in ROWS))

if __name__ == "__main__": unittest.main()
