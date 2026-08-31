type SeedRow = [string,string,string,string,string,string,string,number,string,number|null,string];

const rows: SeedRow[] = [
  ["LA","Vientiane","foodpanda-la","Foodpanda Laos","la-enoki-pack","金针菇 1包","enoki",14000,"LAK",null,"https://www.foodpanda.la/en/restaurant/xf3w/iimsuk-edrii/reviews"],
  ["LA","Vientiane","foodpanda-la","Foodpanda Laos","la-shimeji-pack","真姬菇 1包","shimeji",18000,"LAK",null,"https://www.foodpanda.la/en/restaurant/xf3w/iimsuk-edrii/reviews"],
  ["VN","Ho Chi Minh City","tiki-vn","Tiki","vn-shiitake-50a","干香菇 50g","shiitake",38500,"VND",50,"https://tiki.vn/cua-hang/nam-ly-tuong"],
  ["VN","Ho Chi Minh City","tiki-vn","Tiki","vn-shiitake-100a","干香菇 100g","shiitake",74800,"VND",100,"https://tiki.vn/bestsellers/thuc-pham-kho-khac/c8294"],
  ["VN","Ho Chi Minh City","tiki-vn","Tiki","vn-shiitake-50b","山地干香菇 50g","shiitake",39600,"VND",50,"https://tiki.vn/search?q=n%E1%BA%A5m+h%C6%B0%C6%A1ng+kh%C3%B4"],
  ["VN","Ho Chi Minh City","tiki-vn","Tiki","vn-shiitake-60","干香菇 60g","shiitake",59400,"VND",60,"https://tiki.vn/cua-hang/nam-ly-tuong"],
  ["VN","Ho Chi Minh City","tiki-vn","Tiki","vn-shiitake-100b","精选干香菇 100g","shiitake",50000,"VND",100,"https://tiki.vn/nam-huong-say-kho-dac-biet-100g-special-dried-shiitake-mushrooms-p129576392.html"],
  ["VN","Ho Chi Minh City","tiki-vn","Tiki","vn-wood-ear-100","干木耳 100g","wood_ear",29700,"VND",100,"https://tiki.vn/search?q=n%E1%BA%A5m+h%C6%B0%C6%A1ng+kh%C3%B4"],
  ["VN","Ho Chi Minh City","tiki-vn","Tiki","vn-snow-70","干银耳 70g","snow_fungus",61600,"VND",70,"https://tiki.vn/bestsellers/thuc-pham-kho-khac/c8294"],
  ["TH","Bangkok","bigc-th","Big C Online","th-shiitake-100","鲜香菇 100g","shiitake",29,"THB",100,"https://www.bigc.co.th/group/hyp-mushroom"],
  ["TH","Bangkok","bigc-th","Big C Online","th-enoki-500","鲜金针菇 500g","enoki",25,"THB",500,"https://www.bigc.co.th/group/hyp-mushroom"],
  ["TH","Bangkok","bigc-th","Big C Online","th-enoki-200","鲜金针菇 200g","enoki",14,"THB",200,"https://www.bigc.co.th/product/enokitake-mushroom-200-g.27495"],
  ["TH","Bangkok","bigc-th","Big C Online","th-button-150a","鲜双孢菇 150g","button_mushroom",74,"THB",150,"https://www.bigc.co.th/group/hyp-mushroom"],
  ["TH","Bangkok","bigc-th","Big C Online","th-button-150b","鲜褐色双孢菇 150g","button_mushroom",99,"THB",150,"https://www.bigc.co.th/group/hyp-mushroom"],
  ["TH","Bangkok","bigc-th","Big C Online","th-wood-ear-200","鲜木耳 200g","wood_ear",39,"THB",200,"https://www.bigc.co.th/group/hyp-mushroom"],
  ["TH","Bangkok","bigc-th","Big C Online","th-snow-100","鲜银耳 100g","snow_fungus",17,"THB",100,"https://www.bigc.co.th/group/hyp-mushroom"],
  ["TH","Bangkok","makro-pro-th","Makro PRO","th-enoki-1000","鲜金针菇 1kg","enoki",57,"THB",1000,"https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms"],
  ["TH","Bangkok","makro-pro-th","Makro PRO","th-king-1000","鲜杏鲍菇 1kg","king_oyster_mushroom",65,"THB",1000,"https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms"],
  ["TH","Bangkok","makro-pro-th","Makro PRO","th-enoki-200b","鲜金针菇 200g","enoki",15,"THB",200,"https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms"],
  ["TH","Bangkok","makro-pro-th","Makro PRO","th-enoki-500b","鲜金针菇 500g","enoki",29,"THB",500,"https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms"],
  ["TH","Bangkok","makro-pro-th","Makro PRO","th-shiitake-300","鲜香菇 300g","shiitake",69,"THB",300,"https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms"],
  ["TH","Bangkok","makro-pro-th","Makro PRO","th-king-500","鲜杏鲍菇 500g","king_oyster_mushroom",49,"THB",500,"https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms"],
  ["TH","Bangkok","makro-pro-th","Makro PRO","th-shiitake-500","鲜香菇 500g","shiitake",220,"THB",500,"https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms"],
  ["TH","Bangkok","makro-pro-th","Makro PRO","th-button-200","鲜褐色双孢菇 200g","button_mushroom",75,"THB",200,"https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms"],
  ["TH","Bangkok","makro-pro-th","Makro PRO","th-wood-ear-200b","鲜木耳 200g","wood_ear",27,"THB",200,"https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms"],
  ["TH","Bangkok","makro-pro-th","Makro PRO","th-oyster-200","鲜平菇 200g","oyster_mushroom",29,"THB",200,"https://www.makro.pro/th/p/858816-6976620495043"],
  ["MM","Yangon","foodpanda-mm","Capital Hypermarket","mm-snow-pack","鲜银耳 1包","snow_fungus",7500,"MMK",null,"https://www.foodpanda.com.mm/shop/z2su/capital-hypermarket-h001-dawbon-z2su"],
  ["MM","Yangon","foodpanda-mm","Capital Hypermarket","mm-shimeji-125","白真姬菇 125g","shimeji",6700,"MMK",125,"https://www.foodpanda.com.mm/shop/z2su/capital-hypermarket-h001-dawbon-z2su"],
  ["KH","Phnom Penh","aplus-foodpanda-kh","Aplus Fresh Shop","kh-shimeji-white-200","白真姬菇 200g","shimeji",0.90,"USD",200,"https://www.foodpanda.com.kh/en/shop/vkcs/aplus-fresh-shop"],
  ["KH","Phnom Penh","aplus-foodpanda-kh","Aplus Fresh Shop","kh-shimeji-brown-200","褐色真姬菇 200g","shimeji",0.90,"USD",200,"https://www.foodpanda.com.kh/en/shop/vkcs/aplus-fresh-shop"],
  ["KH","Phnom Penh","aplus-foodpanda-kh","Aplus Fresh Shop","kh-shiitake-200","鲜香菇 200g","shiitake",2.15,"USD",200,"https://www.foodpanda.com.kh/en/shop/vkcs/aplus-fresh-shop"],
  ["KH","Phnom Penh","aplus-foodpanda-kh","Aplus Fresh Shop","kh-enoki-200a","鲜金针菇 200g","enoki",0.90,"USD",200,"https://www.foodpanda.com.kh/en/shop/vkcs/aplus-fresh-shop"],
  ["KH","Phnom Penh","lucky-foodpanda-kh","Lucky Express","kh-enoki-200b","鲜金针菇 200g","enoki",0.76,"USD",200,"https://www.foodpanda.com.kh/en/shop/nyc8/lucky-express-kob-srov-kouk-roka"],
  ["KH","Phnom Penh","lucky-foodpanda-kh","Lucky Express","kh-button-200","鲜双孢菇 200g","button_mushroom",2.39,"USD",200,"https://www.foodpanda.com.kh/shop/yss5/lucky-express-200r-wat-toul"],
  ["KH","Phnom Penh","eplus-foodpanda-kh","Eplus Supermart","kh-enoki-200c","鲜金针菇 200g","enoki",0.70,"USD",200,"https://www.foodpanda.com.kh/shop/vnsf/eplus-supermart"],
  ["KH","Phnom Penh","aeon-foodpanda-kh","AEON Mean Chey","kh-king-300","鲜杏鲍菇 300g","king_oyster_mushroom",3.48,"USD",300,"https://www.foodpanda.com.kh/en/shop/uyxd/aeon-mean-chey-supermarket"]
];

const speciesNames: Record<string,string> = {button_mushroom:"双孢菇",oyster_mushroom:"平菇",shiitake:"香菇",enoki:"金针菇",king_oyster_mushroom:"杏鲍菇",shimeji:"真姬菇",wood_ear:"木耳",snow_fungus:"银耳"};
const timezones: Record<string,string> = {LA:"Asia/Vientiane",VN:"Asia/Ho_Chi_Minh",TH:"Asia/Bangkok",MM:"Asia/Yangon",KH:"Asia/Phnom_Penh"};
const rates: Record<string,number> = {LAK:22487.699349,VND:26073.33318,THB:33.159447,MMK:3658,USD:1};

export async function ensureSeaPriceSeed(db:D1Database){
  const found=await db.prepare("SELECT COUNT(*) AS n FROM products WHERE country IN ('LA','VN','TH','MM','KH')").first<{n:number}>();
  if(Number(found?.n??0)>=rows.length)return;
  const now=Date.now(),date="2026-08-28",statements:D1PreparedStatement[]=[];
  for(const [country,city,platformId,platformName,sku,title,species,price,currency,grams,url] of rows){
    const point=`${country}_RETAIL_01`,product=`${platformId}:${point}:${sku}`,kg=grams?grams/1000:null,rate=rates[currency],localKg=kg?price/kg:null;
    statements.push(
      db.prepare("INSERT INTO species(id,name_zh,name_en,dictionary_version,review_status) VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name_zh=excluded.name_zh").bind(species,speciesNames[species],species,"v1","published"),
      db.prepare("INSERT INTO platforms(id,name,country,collection_method,status,updated_at) VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,country=excluded.country,status='active',updated_at=excluded.updated_at").bind(platformId,platformName,country,"公开零售页面","active",now),
      db.prepare("INSERT INTO collection_points(id,country,city,platform_id,timezone,active,public_label) VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET active=1,public_label=excluded.public_label").bind(point,country,city,platformId,timezones[country],1,city),
      db.prepare("INSERT INTO products(id,platform_id,platform_product_id,collection_point_id,country,city,product_url,original_title,original_language,species_id,product_form,classification_status,classification_confidence,classification_evidence,first_seen_at,last_seen_at,active) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(platform_id,collection_point_id,platform_product_id) DO UPDATE SET original_title=excluded.original_title,species_id=excluded.species_id,classification_status='classified',last_seen_at=excluded.last_seen_at,active=1").bind(product,platformId,sku,point,country,city,url,title,"zh",species,"fresh","classified",0.9,JSON.stringify({rule:"公开商品名称与价格匹配"}),now,now,1),
      db.prepare("INSERT INTO price_observations(id,product_id,observed_at,observation_date,current_price,currency,package_value,package_unit,normalized_quantity_kg,normalized_price_per_kg,price_usd,usd_rate_local_per_usd,fx_source,in_stock,raw_price_text,source_url,source_type,collection_status,validation_status,sanity_outlier,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(product_id,observation_date) DO UPDATE SET current_price=excluded.current_price,normalized_price_per_kg=excluded.normalized_price_per_kg,price_usd=excluded.price_usd,validation_status='valid'").bind(`${product}:${date}`,product,now,date,price,currency,grams,"g",kg,localKg,price/rate,rate,"2026-08-31 汇率参考",1,String(price),url,"公开挂牌价","collected","valid",0,now)
    );
  }
  for(let i=0;i<statements.length;i+=80)await db.batch(statements.slice(i,i+80));
}
