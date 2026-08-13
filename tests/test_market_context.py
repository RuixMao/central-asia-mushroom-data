import sys,unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0,"pipeline")
import fetch_market_context as market

class MarketContextTest(unittest.TestCase):
 def test_country_must_appear_in_title(self):
  self.assertTrue(market._matches_country("TJ","Tajikistan advances food systems"))
  self.assertFalse(market._matches_country("TJ","Fiji restores its forest landscape"))

 def test_country_inference_uses_exact_host_and_unique_title_match(self):
  self.assertEqual(market._infer_country("Agriculture support announced","www.gov.kz"),"KZ")
  self.assertEqual(market._infer_country("Tajikistan advances food systems","www.fao.org"),"TJ")
  self.assertIsNone(market._infer_country("Fiji restores its forest landscape","www.fao.org"))
  self.assertIsNone(market._infer_country("Kazakhstan and Uzbekistan trade talks","www.fao.org"))
  self.assertIsNone(market._infer_country("Agriculture support announced","gov.kz.evil.example"))

 def test_malformed_feed_is_isolated(self):
  response=type("Response",(),{"content":b"<rss><broken>"})()
  with patch.object(market,"safe_get",return_value=response):
   self.assertEqual(market._feed("KZ"),[])

if __name__=="__main__":unittest.main()
