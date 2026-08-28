"""Publish traceable Laos/Myanmar online mushroom prices under the relaxed policy."""
import datetime as dt
import hashlib

from utils import log, post_to_site

DATE = "2026-08-28"
FX = {"LAK": 22420.0, "MMK": 3658.0}
FX_SOURCE = {
    "LAK": "Investing.com USD/LAK 2026-08-28",
    "MMK": "Myanmar Business Journal market-trading rate 2026-08-26",
}

# country, city, platform, product, species, form, spec, price, regular, grams, url, grade, notes
ROWS = [
 ("LA","Vientiane","Han Ping Bae Doy Vang / foodpanda","Fried Enoki Mushrooms / 炸金针菇","enoki","prepared_food","1份（页面未标重量）",90000,None,None,"https://www.foodpanda.la/en/restaurant/lj92/aan-piingeibd-nywngwiw","A","线上餐饮零售价；未折算"),
 ("LA","Vientiane","Nea Tum Zap / foodpanda","Lao Spicy Enoki Mushroom Salad / 老挝辣金针菇沙拉","enoki","prepared_food","1份（页面未标重量）",40500,45000,None,"https://www.foodpanda.la/en/restaurant/c4ut/einahameisb","A","促销价；线上餐饮零售价；未折算"),
 ("LA","Vientiane","Tina Cheese Shake / foodpanda","Crispy battered enoki mushrooms / 脆炸金针菇","enoki","prepared_food","1份（页面未标重量）",29750,35000,None,"https://www.foodpanda.la/en/restaurant/tyiw/hiinaa-siis-esk","A","促销价；线上餐饮零售价；未折算"),
 ("LA","Vientiane","Naked Espresso Common Space / foodpanda","Deep Fried Eryngii Mushroom / 炸杏鲍菇","king_oyster_mushroom","prepared_food","1份（页面未标重量）",49500,55000,None,"https://www.foodpanda.la/en/restaurant/xhkn/naked-espresso-common-space/reviews","A","促销价；线上餐饮零售价；未折算"),
 ("LA","Vientiane","Naked Espresso Common Space / foodpanda","Crispy Enoki Mushroom / 脆炸金针菇","enoki","prepared_food","1份（页面未标重量）",49500,55000,None,"https://www.foodpanda.la/en/restaurant/xhkn/naked-espresso-common-space/reviews","A","促销价；线上餐饮零售价；未折算"),
 ("LA","Vientiane","MK Restaurant Watnak / foodpanda","Enoki Mushrooms with Shabu Pork / 金针菇涮猪肉卷","enoki","prepared_food","5个",29000,None,None,"https://www.foodpanda.la/en/restaurant/zt09/mk-restaurant-wdnaak-zt09","A","混合菜品；未折算"),
 ("LA","Vientiane","Nuan / foodpanda","Grilled Oringi Mushroom With Spicy Sauce / 辣酱烤杏鲍菇","king_oyster_mushroom","prepared_food","1份（页面未标重量）",35340,38000,None,"https://www.foodpanda.la/en/restaurant/v5mq/nwn-nuan/reviews","A","促销价；未折算"),
 ("LA","Vientiane","Nuan / foodpanda","Fried Enoki Mushroom / 炸金针菇","enoki","prepared_food","1份（页面未标重量）",55800,60000,None,"https://www.foodpanda.la/en/restaurant/v5mq/nwn-nuan/reviews","A","促销价；未折算"),
 ("LA","Vientiane","Im Souk Dairy / foodpanda","Enoki Mushroom / 金针菇","enoki","fresh","1包（页面未标重量）",14000,None,None,"https://www.foodpanda.la/en/restaurant/xf3w/iimsuk-edrii/reviews","A","生鲜包；未折算"),
 ("LA","Vientiane","Im Souk Dairy / foodpanda","Shimeji Mushroom / 真姬菇","shimeji","fresh","1包（页面未标重量）",18000,None,None,"https://www.foodpanda.la/en/restaurant/xf3w/iimsuk-edrii/reviews","A","生鲜包；未折算"),
 ("LA","Vientiane","Ping Kai Seno / foodpanda","Stir-fried Mixed Mushroom / 炒杂菌","mixed_mushroom","prepared_food","1份（页面未标重量）",119000,None,None,"https://www.foodpanda.la/en/restaurant/m3al/piingaikeson-hn-ngai","A","混合菌菇菜品；未折算"),
 ("LA","Vientiane","Ping Kai Seno / foodpanda","Stir-fried Enoki Mushroom / 炒金针菇","enoki","prepared_food","1份（页面未标重量）",79000,None,None,"https://www.foodpanda.la/en/restaurant/m3al/piingaikeson-hn-ngai","A","未折算"),
 ("LA","Luang Prabang","Ping Jeen Zap / foodpanda","Meat Wrapped Enoki Mushroom / 肉卷金针菇","enoki","prepared_food","1串",8000,10000,None,"https://www.foodpanda.la/en/restaurant/y82m/aanpiingchiineisbwiailechoaaekoaa-3-7-9/reviews","A","促销价；未折算"),
 ("LA","Luang Prabang","Ping Jeen Zap / foodpanda","Shiitake Mushroom / 烤香菇","shiitake","prepared_food","1串",4000,5000,None,"https://www.foodpanda.la/en/restaurant/y82m/aanpiingchiineisbwiailechoaaekoaa-3-7-9/reviews","A","促销价；未折算"),
 ("LA","Luang Prabang","Ping Jeen Zap / foodpanda","Eringi Mushroom / 烤杏鲍菇","king_oyster_mushroom","prepared_food","1串",4000,5000,None,"https://www.foodpanda.la/en/restaurant/y82m/aanpiingchiineisbwiailechoaaekoaa-3-7-9/reviews","A","促销价；未折算"),
 ("LA","Luang Prabang","Ping Jeen Zap / foodpanda","Enoki Mushroom / 烤金针菇","enoki","prepared_food","1串",4000,5000,None,"https://www.foodpanda.la/en/restaurant/y82m/aanpiingchiineisbwiailechoaaekoaa-3-7-9/reviews","A","促销价；未折算"),
 ("LA","Vientiane","Joy 3434 Zap Nua / foodpanda","Fried Enoki Mushroom / 炸金针菇","enoki","prepared_food","1份（页面未标重量）",41650,49000,None,"https://www.foodpanda.la/en/restaurant/bv29/aan-ch-ny-3434-eisbnow-bv29/reviews","A","促销价；未折算"),
 ("LA","Vientiane","Joy 3434 Zap Nua / foodpanda","Stir-fried Mixed Mushrooms / 炒杂菌","mixed_mushroom","prepared_food","1份（页面未标重量）",50150,59000,None,"https://www.foodpanda.la/en/restaurant/bv29/aan-ch-ny-3434-eisbnow-bv29/reviews","A","促销价；混合菌菇；未折算"),
]

for grams, price in [(200,44000),(300,66000),(400,88000),(500,110000),(600,132000),(700,154000),(800,176000),(900,198000),(1000,220000),(1300,186000)]:
 ROWS.append(("LA","Vientiane","Yum Jeen Yum Derk / foodpanda",f"Chinese Mala Yum Mixed Vegetables and Mixed Meat {grams}g / 麻辣杂菜杂肉（含金针菇）{grams}g","mixed_mushroom","prepared_food",f"{grams}g/份",price,None,grams,"https://www.foodpanda.la/en/restaurant/q90l/nyamchiinnyamedik/reviews","A","整份含金针菇及其他食材；USD/kg仅代表整份菜品"))

ROWS += [
 ("MM","Yangon","Capital Hypermarket Dawbon / foodpanda","Thai Silver Mushroom 1 Packet / 泰国银耳菇","snow_fungus","fresh","1包（页面未标重量）",7500,None,None,"https://www.foodpanda.com.mm/shop/z2su/capital-hypermarket-h001-dawbon-z2su","A","生鲜包；未折算"),
 ("MM","Yangon","Capital Hypermarket Dawbon / foodpanda","White Shimeji Mushroom 125g / 白真姬菇","shimeji","fresh","125g",6700,None,125,"https://www.foodpanda.com.mm/shop/z2su/capital-hypermarket-h001-dawbon-z2su","A","生鲜定量包装"),
 ("MM","Yangon","Go Green Myanmar / foodpanda","Mushroom 200g / 蘑菇","unspecified_mushroom","fresh","200g",3300,None,200,"https://www.foodpanda.com.mm/en/shop/s5kk/go-green-myanmar","A","页面未标具体菌种"),
 ("MM","Yangon","Summer Fruit / foodpanda","Pounded Enoki Mushroom / 凉拌金针菇","enoki","prepared_food","1份（页面未标重量）",5000,None,None,"https://www.foodpanda.com.mm/en/restaurant/xlsp/summer-fruit-xlsp","A","未折算"),
 ("MM","Yangon","Summer Fruit / foodpanda","Spicy Enoki Mushroom Salad / 辣味金针菇沙拉","enoki","prepared_food","1份（页面未标重量）",4000,None,None,"https://www.foodpanda.com.mm/en/restaurant/xlsp/summer-fruit-xlsp","A","未折算"),
 ("MM","Yangon","Shan Lay / foodpanda","Pounded Snow Fungus Salad / 凉拌银耳","snow_fungus","prepared_food","1份（页面未标重量）",3500,None,None,"https://www.foodpanda.com.mm/en/restaurant/m3pg/r-m-le","A","未折算"),
 ("MM","Yangon","Shan Lay / foodpanda","Pounded Enoki Mushroom / 凉拌金针菇","enoki","prepared_food","1份（页面未标重量）",4000,None,None,"https://www.foodpanda.com.mm/en/restaurant/m3pg/r-m-le","A","未折算"),
 ("MM","Yangon","Day 20 / foodpanda","Thai Style Pounded Enoki Mushroom / 泰式金针菇沙拉","enoki","prepared_food","1份（页面未标重量）",5500,None,None,"https://www.foodpanda.com.mm/en/restaurant/bizu/day-20","A","未折算"),
 ("MM","Yangon","Kaung Food Streat / foodpanda","Pounded Enoki Mushroom / 凉拌金针菇","enoki","prepared_food","1份（页面未标重量）",6500,None,None,"https://www.foodpanda.com.mm/en/restaurant/ms7x/kaung-food-streat","A","未折算"),
 ("MM","Yangon","Kaung Food Streat / foodpanda","Stir Fried Water Spinach with Mushroom / 菌菇炒空心菜","unspecified_mushroom","prepared_food","1份（页面未标重量）",6000,None,None,"https://www.foodpanda.com.mm/en/restaurant/ms7x/kaung-food-streat","A","页面未标具体菌种；未折算"),
 ("MM","Yangon","Win Metta / foodpanda","Pounded Enoki Mushroom / 凉拌金针菇","enoki","prepared_food","1份（页面未标重量）",4250,5000,None,"https://www.foodpanda.com.mm/en/restaurant/fxei/wng-mettttaacaa-ph-y-cun","A","促销价；店铺页面标记关闭；历史价；未折算"),
 ("MM","Yangon","Shwe Mon Gyi / foodpanda","Snow Fungus Salad / 银耳沙拉","snow_fungus","prepared_food","1份（页面未标重量）",7000,None,None,"https://www.foodpanda.com.mm/en/restaurant/vlp0/r-em-n-k-ii-phaaluud-diuminiun-ng-caa-ph-y-cun","A","店铺页面标记关闭；历史价；未折算"),
 ("MM","Yangon","Shwe Mon Gyi / foodpanda","Enoki Mushroom Som Tum / 金针菇沙拉","enoki","prepared_food","1份（页面未标重量）",5500,None,None,"https://www.foodpanda.com.mm/en/restaurant/vlp0/r-em-n-k-ii-phaaluud-diuminiun-ng-caa-ph-y-cun","A","店铺页面标记关闭；历史价；未折算"),
 ("MM","Yangon","Yum Thai / foodpanda","Enoki Mushroom with Oyster Sauce / 蚝油金针菇","enoki","prepared_food","1份（页面未标重量）",10400,None,None,"https://www.foodpanda.com.mm/en/restaurant/t0ho/yum-thai","A","起价；未折算"),
 ("MM","Yangon","Yum Thai / foodpanda","Stir Fried Enoki Mushroom / 炒金针菇","enoki","prepared_food","1份（页面未标重量）",10400,None,None,"https://www.foodpanda.com.mm/en/restaurant/t0ho/yum-thai","A","未折算"),
 ("MM","Yangon","Together Food & BBQ / foodpanda","Enoki Mushroom / 炒金针菇","enoki","prepared_food","1份（页面未标重量）",6500,None,None,"https://www.foodpanda.com.mm/en/restaurant/s2hn/together-food-and-bbq","A","未折算"),
 ("MM","Yangon","Together Food & BBQ / foodpanda","Stir Fried Water Spinach with Mushroom / 菌菇炒空心菜","unspecified_mushroom","prepared_food","1份（页面未标重量）",6500,None,None,"https://www.foodpanda.com.mm/en/restaurant/s2hn/together-food-and-bbq","A","页面未标具体菌种；未折算"),
 ("MM","Yangon","San Yati / foodpanda","Pounded Enoki Mushroom / 凉拌金针菇","enoki","prepared_food","1份（页面未标重量）",5500,None,None,"https://www.foodpanda.com.mm/en/restaurant/pq9j/cnrttii-ang-diuk-k-k-eaa-n-ng-atheaang","A","未折算"),
 ("MM","Yangon","Nyaungdon Road Cold Shop / foodpanda","Steamed Enoki Mushroom with Lime / 青柠蒸金针菇","enoki","prepared_food","1份（页面未标重量）",11000,None,None,"https://www.foodpanda.com.mm/en/restaurant/iycl/nnyeaang-ttun-lm-thip-aae-chiung","A","未折算"),
 ("MM","Yangon","Green Mala / foodpanda","Pounded Enoki Mushroom / 凉拌金针菇","enoki","prepared_food","1份（页面未标重量）",7000,None,None,"https://www.foodpanda.com.mm/en/restaurant/k7pp/cim-ln-ciup-e-maalaahng-chiung","A","未折算"),
 ("MM","Yangon","Green Mala / foodpanda","Stir Fried Water Spinach with Mushroom / 菌菇炒空心菜","unspecified_mushroom","prepared_food","1份（页面未标重量）",4500,None,None,"https://www.foodpanda.com.mm/en/restaurant/k7pp/cim-ln-ciup-e-maalaahng-chiung","A","页面未标具体菌种；未折算"),
 ("MM","Yangon","Yamasan Asian Food / foodpanda","Sour and Spicy Enoki Mushroom with Rice / 酸辣金针菇盖饭","enoki","prepared_food","1份（页面未标重量）",9000,None,None,"https://www.foodpanda.com.mm/en/restaurant/fwa3/nyii-k-eaa-yamasan-asian-food","A","混合菜品；未折算"),
]

def run():
 now = dt.datetime.now(dt.timezone.utc).isoformat()
 for country, city, platform, title, species, form, spec, price, regular, grams, url, grade, notes in ROWS:
  source = "foodpanda-la" if country == "LA" else "foodpanda-mm"
  key = hashlib.sha1(f"{country}|{platform}|{title}|{spec}|{price}".encode()).hexdigest()[:16]
  rate = FX["LAK" if country == "LA" else "MMK"]
  currency = "LAK" if country == "LA" else "MMK"
  kg = grams / 1000 if grams else None
  usdkg = round(price / kg / rate, 2) if kg else None
  data = {"product_key": f"{source}:{key}", "species_id": species, "original_title": title,
          "product_form": form, "product_shape": "mixed" if form == "prepared_food" else "whole",
          "processing_state": form, "packaging_type": "portion" if form == "prepared_food" else "packaged",
          "package_display": spec, "platform_name": platform, "status": "live", "validation_status": "valid",
          "price_local": price, "regular_price_local": regular, "currency": currency,
          "price_usd": round(price / rate, 2), "normalized_price_usd_per_kg": usdkg,
          "observed_at": DATE, "retrieved_at": now, "source_url": url,
          "source_type": "电商商品页", "grade": grade, "notes": notes,
          "fx_rate_local_per_usd": rate, "fx_source": FX_SOURCE[currency]}
  post_to_site("/api/ingest/snapshot", {"metric":"price_retail","country":country,"source":source,"data":data})
 log(f"relaxed Laos/Myanmar retail rows written: {len(ROWS)}")

if __name__ == "__main__": run()
