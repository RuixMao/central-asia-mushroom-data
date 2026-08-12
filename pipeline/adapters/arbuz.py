import json
from .base import ProductAdapter

class ArbuzAdapter(ProductAdapter):
 def parse(self,response):
  data=response.json() if "json" in response.headers.get("content-type","") else json.loads(response.text)
  product=data.get("product",data)
  return {**self.config,"original_title":product["name"],"current_price":float(product["price"]),"regular_price":product.get("old_price"),"in_stock":product.get("available",True),"raw_price_text":str(product["price"])}
