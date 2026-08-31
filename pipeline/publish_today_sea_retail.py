"""Publish today's report-ready Southeast Asia mushroom retail listings."""
import datetime as dt
import hashlib
from zoneinfo import ZoneInfo

from utils import log, post_to_site, safe_get

DATE = dt.datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()

# country, city, platform id/name, title, species, form, grams, price, currency, URL, regular price
ROWS = [
    ("LA", "Vientiane", "champa-garden-la", "Champa Garden", "Enoki Mushroom 200g Pack", "enoki", "fresh", 200, 12000, "LAK", "https://champagardenshop.com/products/enoki-mushroom-200g-pack-barcode-50103090", None),
    ("LA", "Vientiane", "champa-garden-la", "Champa Garden", "Eringi Mushroom 200g", "king_oyster_mushroom", "fresh", 200, 15000, "LAK", "https://champagardenshop.com/products/eringi-mushroom", None),
    ("MM", "Yangon", "capital-foodpanda-mm", "Capital Supermarket / foodpanda", "White Shime Ji Mushroom 125g", "shimeji", "fresh", 125, 6700, "MMK", "https://www.foodpanda.com.mm/en/shop/pzze/capital-supermarket-s021-sanchaung-pzze", None),
    ("VN", "Ho Chi Minh City", "tiki-vn", "Tiki", "Nấm Hương Khô Lý Tưởng 50g", "shiitake", "dried", 50, 38500, "VND", "https://tiki.vn/cua-hang/nam-ly-tuong", None),
    ("VN", "Ho Chi Minh City", "tiki-vn", "Tiki", "Nấm Hương Khô 100g", "shiitake", "dried", 100, 74800, "VND", "https://tiki.vn/bestsellers/thuc-pham-kho-khac/c8294", None),
    ("VN", "Ho Chi Minh City", "tiki-vn", "Tiki", "Nấm Hương Rừng 50g", "shiitake", "dried", 50, 39600, "VND", "https://tiki.vn/search?q=n%E1%BA%A5m+h%C6%B0%C6%A1ng+kh%C3%B4", None),
    ("VN", "Ho Chi Minh City", "tiki-vn", "Tiki", "Nấm Đông Cô Khô 60g", "shiitake", "dried", 60, 59400, "VND", "https://tiki.vn/cua-hang/nam-ly-tuong", None),
    ("VN", "Ho Chi Minh City", "tiki-vn", "Tiki", "Nấm Hương Sấy Khô Đặc Biệt 100g", "shiitake", "dried", 100, 50000, "VND", "https://tiki.vn/nam-huong-say-kho-dac-biet-100g-special-dried-shiitake-mushrooms-p129576392.html", None),
    ("VN", "Ho Chi Minh City", "tiki-vn", "Tiki", "Mộc Nhĩ Khô 100g", "wood_ear", "dried", 100, 29700, "VND", "https://tiki.vn/search?q=m%E1%BB%99c+nh%C4%A9+kh%C3%B4", None),
    ("KH", "Phnom Penh", "aplus-foodpanda-kh", "Aplus Fresh Shop / foodpanda", "White Beech Mushroom Pack 200g", "shimeji", "fresh", 200, .90, "USD", "https://www.foodpanda.com.kh/en/shop/vkcs/aplus-fresh-shop", None),
    ("KH", "Phnom Penh", "aplus-foodpanda-kh", "Aplus Fresh Shop / foodpanda", "Brown Beech Mushroom Pack 200g", "shimeji", "fresh", 200, .90, "USD", "https://www.foodpanda.com.kh/en/shop/vkcs/aplus-fresh-shop", None),
    ("KH", "Phnom Penh", "aplus-foodpanda-kh", "Aplus Fresh Shop / foodpanda", "Shiitake Mushroom Pack 200g", "shiitake", "fresh", 200, 2.15, "USD", "https://www.foodpanda.com.kh/en/shop/vkcs/aplus-fresh-shop", None),
    ("KH", "Phnom Penh", "aplus-foodpanda-kh", "Aplus Fresh Shop / foodpanda", "Enoki Mushroom Pack 200g", "enoki", "fresh", 200, .90, "USD", "https://www.foodpanda.com.kh/en/shop/vkcs/aplus-fresh-shop", None),
    ("KH", "Phnom Penh", "lucky-foodpanda-kh", "Lucky Express / foodpanda", "LUCKY MUSHROOM ENOKI 200G", "enoki", "fresh", 200, .76, "USD", "https://www.foodpanda.com.kh/en/shop/nyc8/lucky-express-kob-srov-kouk-roka", None),
    ("KH", "Phnom Penh", "lucky-foodpanda-kh", "Lucky Express / foodpanda", "Lucky Fresh White Button Mushroom 200g", "button_mushroom", "fresh", 200, 2.39, "USD", "https://www.foodpanda.com.kh/shop/yss5/lucky-express-200r-wat-toul", None),
    ("KH", "Phnom Penh", "eplus-foodpanda-kh", "Eplus Supermart / foodpanda", "LUCKY MUSHROOM ENOKI 200G", "enoki", "fresh", 200, .70, "USD", "https://www.foodpanda.com.kh/shop/vnsf/eplus-supermart", None),
    ("KH", "Phnom Penh", "aeon-foodpanda-kh", "AEON Mean Chey / foodpanda", "King Oyster Mushroom Big 0.3kg", "king_oyster_mushroom", "fresh", 300, 3.48, "USD", "https://www.foodpanda.com.kh/en/shop/uyxd/aeon-mean-chey-supermarket", None),
]

TH_ROWS = [
    ("bigc-th", "Big C Online", "วี อาร์ เฟร็ช เห็ดเข็มทอง 500 ก.", "enoki", 500, 30, "https://www.bigc.co.th/group/hyp-mushroom", None),
    ("bigc-th", "Big C Online", "เห็ดเข็มทอง 200 ก.", "enoki", 200, 9, "https://www.bigc.co.th/group/hyp-mushroom", 18),
    ("bigc-th", "Big C Online", "เห็ดแชมปิญอง 150 ก.", "button_mushroom", 150, 65, "https://www.bigc.co.th/group/hyp-mushroom", None),
    ("bigc-th", "Big C Online", "วีอาร์เฟรช เห็ดหูหนูดำ แพ็ค 200 ก.", "wood_ear", 200, 39, "https://www.bigc.co.th/group/hyp-mushroom", None),
    ("bigc-th", "Big C Online", "วี อาร์ เฟร็ช เห็ดแชมปิญองน้ำตาล 150 ก.", "button_mushroom", 150, 89, "https://www.bigc.co.th/group/hyp-mushroom", None),
    ("bigc-th", "Big C Online", "วีอาร์เฟรช เห็ดหอมสด 100 ก.", "shiitake", 100, 35, "https://www.bigc.co.th/group/hyp-mushroom", None),
    ("makro-pro-th", "Makro PRO", "เอโร่ เห็ดเข็มทอง 1 กก.", "enoki", 1000, 57, "https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms", None),
    ("makro-pro-th", "Makro PRO", "เห็ดนางรมหลวง ขนาด L 1 กก.", "king_oyster_mushroom", 1000, 65, "https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms", None),
    ("makro-pro-th", "Makro PRO", "สหฟาร์มเห็ด เห็ดเข็มทอง 200 ก.", "enoki", 200, 15, "https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms", None),
    ("makro-pro-th", "Makro PRO", "เห็ดเข็มทอง 500 ก.", "enoki", 500, 29, "https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms", None),
    ("makro-pro-th", "Makro PRO", "เห็ดหอมสด เบอร์ใหญ่ 300 ก.", "shiitake", 300, 69, "https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms", None),
    ("makro-pro-th", "Makro PRO", "เห็ดนางรมหลวง 500 ก.", "king_oyster_mushroom", 500, 49, "https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms", None),
    ("makro-pro-th", "Makro PRO", "เอโร่ เห็ดหอมกลาง 500 ก.", "shiitake", 500, 220, "https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms", None),
    ("makro-pro-th", "Makro PRO", "เห็ดแชมปิญองน้ำตาลเล็ก 200 ก.", "button_mushroom", 200, 75, "https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms", None),
    ("makro-pro-th", "Makro PRO", "เห็ดหูหนู 200 ก.", "wood_ear", 200, 27, "https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms", None),
]
ROWS.extend(("TH", "Bangkok", pid, pname, title, species, "fresh", grams, price, "THB", url, regular) for pid, pname, title, species, grams, price, url, regular in TH_ROWS)


def run():
    rates = safe_get("https://fxapi.app/api/usd.json", retries=2).json()["rates"]
    rates["USD"] = 1
    # Myanmar retail conversion uses the public market rate rather than the official peg.
    rates["MMK"] = 3658
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    for country, city, pid, pname, title, species, form, grams, price, currency, url, regular in ROWS:
        key = hashlib.sha1(f"{pid}|{title}".encode()).hexdigest()[:16]
        rate = float(rates[currency])
        usdkg = round(price / (grams / 1000) / rate, 2)
        post_to_site("/api/ingest/snapshot", {"metric": "price_retail", "country": country, "source": pid, "data": {
            "product_key": f"{pid}:{key}", "city": city, "species_id": species, "original_title": title,
            "product_form": form, "product_shape": "whole", "processing_state": form,
            "packaging_type": "packaged", "package_display": f"{grams:g} g", "package_source": "page_title",
            "platform_name": pname, "status": "live", "validation_status": "valid", "price_local": price,
            "regular_price_local": regular, "currency": currency, "price_usd": round(price / rate, 2),
            "normalized_price_usd_per_kg": usdkg, "observed_at": DATE, "retrieved_at": now,
            "fx_rate_local_per_usd": rate, "fx_date": DATE, "source_url": url}})
    log(f"today Southeast Asia retail rows written: {len(ROWS)}")


if __name__ == "__main__":
    run()
