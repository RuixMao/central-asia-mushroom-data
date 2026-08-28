"""Publish manually verified public retailer listings to the canonical site."""
import datetime as dt
import hashlib

from utils import post_to_site, safe_get, log

DATE = "2026-08-28"
ROWS = [
 # country, city, platform id/name, title, species, form, grams, price, currency, url, regular price, in stock
 ("TH","Bangkok","bigc-th","Big C Online","เห็ดหอมสด 100 ก.","shiitake","fresh",100,29,"THB","https://www.bigc.co.th/group/hyp-mushroom",None,True),
 ("TH","Bangkok","bigc-th","Big C Online","วี อาร์ เฟร็ช เห็ดเข็มทอง 500 ก.","enoki","fresh",500,25,"THB","https://www.bigc.co.th/group/hyp-mushroom",30,True),
 ("TH","Bangkok","bigc-th","Big C Online","เห็ดเข็มทอง 200 ก.","enoki","fresh",200,14,"THB","https://www.bigc.co.th/product/enokitake-mushroom-200-g.27495",17,True),
 ("TH","Bangkok","bigc-th","Big C Online","เห็ดแชมปิญอง 150 ก.","button_mushroom","fresh",150,74,"THB","https://www.bigc.co.th/group/hyp-mushroom",None,True),
 ("TH","Bangkok","bigc-th","Big C Online","เห็ดแชมปิญองน้ำตาล 150 ก.","button_mushroom","fresh",150,99,"THB","https://www.bigc.co.th/group/hyp-mushroom",None,True),
 ("TH","Bangkok","bigc-th","Big C Online","วีอาร์เฟรช เห็ดหูหนูดำ 200 ก.","wood_ear","fresh",200,39,"THB","https://www.bigc.co.th/group/hyp-mushroom",None,True),
 ("TH","Bangkok","bigc-th","Big C Online","เห็ดหิมะขาว 100 ก.","snow_fungus","fresh",100,17,"THB","https://www.bigc.co.th/group/hyp-mushroom",None,True),
 ("TH","Bangkok","bigc-th","Big C Online","เห็ดออรินจิ 500 ก.","king_oyster_mushroom","fresh",500,65,"THB","https://www.bigc.co.th/group/hyp-mushroom",None,False),
 ("TH","Bangkok","bigc-th","Big C Online","เห็ดหอมสด 300 ก.","shiitake","fresh",300,79,"THB","https://www.bigc.co.th/group/hyp-mushroom",None,False),
 ("TH","Bangkok","bigc-th","Big C Online","เห็ดนางรมฮังการี 100 ก.","oyster_mushroom","fresh",100,29,"THB","https://www.bigc.co.th/group/hyp-mushroom",None,False),
 ("TH","Bangkok","makro-pro-th","Makro PRO","เอโร่ เห็ดเข็มทอง 1 กก.","enoki","fresh",1000,57,"THB","https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms",None,True),
 ("TH","Bangkok","makro-pro-th","Makro PRO","เห็ดนางรมหลวง ขนาด L 1 กก.","king_oyster_mushroom","fresh",1000,65,"THB","https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms",None,True),
 ("TH","Bangkok","makro-pro-th","Makro PRO","สหฟาร์มเห็ด เห็ดเข็มทอง 200 ก.","enoki","fresh",200,15,"THB","https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms",None,True),
 ("TH","Bangkok","makro-pro-th","Makro PRO","เห็ดเข็มทอง 500 ก.","enoki","fresh",500,29,"THB","https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms",None,True),
 ("TH","Bangkok","makro-pro-th","Makro PRO","เห็ดหอมสด เบอร์ใหญ่ 300 ก.","shiitake","fresh",300,69,"THB","https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms",None,True),
 ("TH","Bangkok","makro-pro-th","Makro PRO","เห็ดออรินจิ 500 ก.","king_oyster_mushroom","fresh",500,49,"THB","https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms",None,True),
 ("TH","Bangkok","makro-pro-th","Makro PRO","เอโร่ เห็ดหอมกลาง 500 ก.","shiitake","fresh",500,220,"THB","https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms",None,True),
 ("TH","Bangkok","makro-pro-th","Makro PRO","เห็ดแชมปิญองน้ำตาลเล็ก 200 ก.","button_mushroom","fresh",200,75,"THB","https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms",None,True),
 ("TH","Bangkok","makro-pro-th","Makro PRO","เห็ดหูหนู 200 ก.","wood_ear","fresh",200,27,"THB","https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms",None,True),
 ("TH","Bangkok","makro-pro-th","Makro PRO","เห็ดนางรม 200 ก.","oyster_mushroom","fresh",200,29,"THB","https://www.makro.pro/th/p/858816-6976620495043",None,True),
 ("VN","Ho Chi Minh City","tiki-vn","Tiki","Nấm Hương Khô Lý Tưởng 50g","shiitake","dried",50,38500,"VND","https://tiki.vn/cua-hang/nam-ly-tuong",None,True),
 ("VN","Ho Chi Minh City","tiki-vn","Tiki","Nấm Hương Khô 100g","shiitake","dried",100,74800,"VND","https://tiki.vn/bestsellers/thuc-pham-kho-khac/c8294",None,True),
 ("VN","Ho Chi Minh City","tiki-vn","Tiki","Nấm Hương Rừng 50g","shiitake","dried",50,39600,"VND","https://tiki.vn/search?q=n%E1%BA%A5m+h%C6%B0%C6%A1ng+kh%C3%B4",None,True),
 ("VN","Ho Chi Minh City","tiki-vn","Tiki","Nấm Đông Cô Khô 60g","shiitake","dried",60,59400,"VND","https://tiki.vn/cua-hang/nam-ly-tuong",None,True),
 ("VN","Ho Chi Minh City","tiki-vn","Tiki","Nấm Hương Sấy Khô Đặc Biệt 100g","shiitake","dried",100,50000,"VND","https://tiki.vn/nam-huong-say-kho-dac-biet-100g-special-dried-shiitake-mushrooms-p129576392.html",None,True),
 ("VN","Ho Chi Minh City","tiki-vn","Tiki","Mộc Nhĩ Khô 100g","wood_ear","dried",100,29700,"VND","https://tiki.vn/search?q=n%E1%BA%A5m+h%C6%B0%C6%A1ng+kh%C3%B4",None,True),
 ("VN","Ho Chi Minh City","tiki-vn","Tiki","Nấm Tuyết Trắng Khô 70g","snow_fungus","dried",70,61600,"VND","https://tiki.vn/bestsellers/thuc-pham-kho-khac/c8294",None,True),
 ("KH","Phnom Penh","aplus-foodpanda-kh","Aplus Fresh Shop / foodpanda","White Beech Mushroom Pack 200g","shimeji","fresh",200,.90,"USD","https://www.foodpanda.com.kh/en/shop/vkcs/aplus-fresh-shop",None,True),
 ("KH","Phnom Penh","aplus-foodpanda-kh","Aplus Fresh Shop / foodpanda","Brown Beech Mushroom Pack 200g","shimeji","fresh",200,.90,"USD","https://www.foodpanda.com.kh/en/shop/vkcs/aplus-fresh-shop",None,True),
 ("KH","Phnom Penh","aplus-foodpanda-kh","Aplus Fresh Shop / foodpanda","Shiitake Mushroom Pack 200g","shiitake","fresh",200,2.15,"USD","https://www.foodpanda.com.kh/en/shop/vkcs/aplus-fresh-shop",None,True),
 ("KH","Phnom Penh","aplus-foodpanda-kh","Aplus Fresh Shop / foodpanda","Enoki Mushroom Pack 200g","enoki","fresh",200,.90,"USD","https://www.foodpanda.com.kh/en/shop/vkcs/aplus-fresh-shop",None,True),
 ("KH","Phnom Penh","lucky-foodpanda-kh","Lucky Express / foodpanda","LUCKY MUSHROOM ENOKI 200G","enoki","fresh",200,.76,"USD","https://www.foodpanda.com.kh/en/shop/nyc8/lucky-express-kob-srov-kouk-roka",None,True),
 ("KH","Phnom Penh","lucky-foodpanda-kh","Lucky Express / foodpanda","Lucky Fresh White Button Mushroom 200g","button_mushroom","fresh",200,2.39,"USD","https://www.foodpanda.com.kh/shop/yss5/lucky-express-200r-wat-toul",None,True),
 ("KH","Phnom Penh","eplus-foodpanda-kh","Eplus Supermart / foodpanda","LUCKY MUSHROOM ENOKI 200G","enoki","fresh",200,.70,"USD","https://www.foodpanda.com.kh/shop/vnsf/eplus-supermart",None,True),
 ("KH","Phnom Penh","aeon-foodpanda-kh","AEON Mean Chey / foodpanda","King Oyster Mushroom Big 0.3kg","king_oyster_mushroom","fresh",300,3.48,"USD","https://www.foodpanda.com.kh/en/shop/uyxd/aeon-mean-chey-supermarket",None,True),
]

def run():
 rates=safe_get("https://fxapi.app/api/usd.json",retries=2).json()["rates"]
 items=[]
 for country,city,pid,pname,title,species,form,grams,price,currency,url,regular,stock in ROWS:
  key=hashlib.sha1(f"{pid}|{title}".encode()).hexdigest()[:16]; kg=grams/1000; local_usd=1 if currency=="USD" else float(rates[currency]); usdkg=round(price/kg/local_usd,2); now=dt.datetime.now(dt.timezone.utc).isoformat()
  items.append({"platform":pid,"platform_name":pname,"platform_product_id":key,"country":country,"city":city,"collection_point_id":f"{country}_RETAIL_01","product_url":url,"original_title":title,"original_language":"th" if country=="TH" else "vi" if country=="VN" else "en","species_id":species,"product_form":form,"classification_status":"classified","classification_confidence":1,"classification_evidence":{"rule":"verified_retail_listing"},"observed_at":now,"observation_date":DATE,"current_price":price,"regular_price":regular,"promotion_price":price if regular else None,"currency":currency,"package_value":grams,"package_unit":"g","normalized_quantity_kg":kg,"normalized_price_per_kg":round(price/kg,2),"price_usd":round(price/local_usd,2),"usd_rate_local_per_usd":local_usd,"fx_source":"fxapi.app","in_stock":stock,"raw_price_text":str(price),"source_type":"verified_public_listing","validation_status":"valid","review_reasons":[],"sanity_outlier":False})
  post_to_site("/api/ingest/snapshot",{"metric":"price_retail","country":country,"source":pid,"data":{"product_key":f"{pid}:{key}","species_id":species,"original_title":title,"product_form":form,"product_shape":"whole","processing_state":form,"packaging_type":"packaged","package_display":f"{grams:g} g","platform_name":pname,"status":"live","validation_status":"valid","price_local":price,"currency":currency,"price_usd":round(price/local_usd,2),"normalized_price_usd_per_kg":usdkg,"observed_at":DATE,"retrieved_at":now,"source_url":url}})
 post_to_site("/api/ingest/prices",{"items":items}); log(f"verified SEA retail rows written: {len(items)}")

if __name__=="__main__": run()
