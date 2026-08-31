type X = {
  c: string;
  s: string;
  n: string;
  v: number;
  cur: string;
  spec: string;
  kg?: number;
  src: string;
  url: string;
  g: string;
  t: string;
  d: string;
  note?: string;
};
const thUrl = "https://www.bigc.co.th/en/group/hyp-mushroom",
  mkTh =
    "https://www.makro.pro/en/c/collections/Yummy%20and%20Healthy%20Mushrooms",
  shTh =
    "https://shopee.co.th/search?keyword=%E0%B9%80%E0%B8%AB%E0%B9%87%E0%B8%94%E0%B8%AB%E0%B8%B9%E0%B8%AB%E0%B8%99%E0%B8%B9";
const th: X[] = [
  {
    s: "shiitake",
    n: "Fresh Shiitake",
    v: 29,
    spec: "100g",
    kg: 0.1,
    src: "Big C",
    url: thUrl,
  },
  {
    s: "shiitake",
    n: "Imported Fresh Shiitake",
    v: 79,
    spec: "300g",
    kg: 0.3,
    src: "Big C",
    url: thUrl,
  },
  {
    s: "shiitake",
    n: "Dried Shiitake",
    v: 680,
    spec: "未标重量",
    src: "Big C",
    url: thUrl,
  },
  {
    s: "shiitake",
    n: "Dried Large Shiitake",
    v: 58,
    spec: "65g",
    kg: 0.065,
    src: "Big C",
    url: "https://www.bigc.co.th/en/product/big-c-dried-mushroom-large-65-g.33231",
  },
  {
    s: "oyster_mushroom",
    n: "Oyster Mushroom",
    v: 65,
    spec: "500g",
    kg: 0.5,
    src: "Big C",
    url: thUrl,
  },
  {
    s: "oyster_mushroom",
    n: "Hungary Oyster Mushroom",
    v: 29,
    spec: "100g",
    kg: 0.1,
    src: "Big C",
    url: thUrl,
  },
  {
    s: "oyster_mushroom",
    n: "Oyster Mushroom",
    v: 59,
    spec: "500g",
    kg: 0.5,
    src: "Makro",
    url: "https://www.makro.pro/en/p/858818-7422341480643",
  },
  {
    s: "oyster_mushroom",
    n: "King Oyster Mushroom L",
    v: 65,
    spec: "1kg",
    kg: 1,
    src: "Makro",
    url: mkTh,
  },
  {
    s: "oyster_mushroom",
    n: "King Oyster Mushroom",
    v: 49,
    spec: "500g",
    kg: 0.5,
    src: "Makro",
    url: mkTh,
  },
  {
    s: "wood_ear",
    n: "Black Jelly Mushroom",
    v: 39,
    spec: "200g",
    kg: 0.2,
    src: "Big C",
    url: thUrl,
  },
  {
    s: "wood_ear",
    n: "Black Jelly Fungus",
    v: 28,
    spec: "100g",
    kg: 0.1,
    src: "Big C",
    url: thUrl,
  },
  {
    s: "wood_ear",
    n: "Wood Ear Fungus",
    v: 27,
    spec: "200g",
    kg: 0.2,
    src: "Makro",
    url: mkTh,
  },
  {
    s: "wood_ear",
    n: "Dried Black Wood Ear",
    v: 190,
    spec: "1kg",
    kg: 1,
    src: "Shopee TH",
    url: shTh,
  },
  {
    s: "wood_ear",
    n: "Dried White Wood Ear",
    v: 55,
    spec: "50g",
    kg: 0.05,
    src: "Shopee TH",
    url: shTh,
  },
  {
    s: "wood_ear",
    n: "Premium Black Wood Ear",
    v: 100,
    spec: "500g",
    kg: 0.5,
    src: "Shopee TH",
    url: shTh,
  },
].map((x) => ({
  ...x,
  c: "TH",
  cur: "THB",
  g: "A",
  t: "正常",
  d: "2026-08-31",
}));
const vnUrl = "https://www.alibaba.com/countrysearch/VN/wood-ear-mushroom.html";
const vn: X[] = [
  {
    s: "oyster_mushroom",
    n: "Oyster Mushrooms",
    v: 60000,
    spec: "250g",
    kg: 0.25,
    src: "ByNature",
    url: "https://bynature.vn/product-category/fruits-vegetables/vegetables/mushroom/",
    g: "A",
  },
  {
    s: "shiitake",
    n: "Shiitake Mushrooms",
    v: 110000,
    spec: "250g",
    kg: 0.25,
    src: "ByNature",
    url: "https://bynature.vn/product-category/fruits-vegetables/vegetables/mushroom/",
    g: "A",
  },
  {
    s: "wood_ear",
    n: "Dried Jelly Ear",
    v: 35000,
    spec: "50g",
    kg: 0.05,
    src: "ByNature",
    url: "https://bynature.vn/product-category/fruits-vegetables/vegetables/mushroom/",
    g: "A",
  },
  {
    s: "oyster_mushroom",
    n: "Nấm Bào Ngư Trắng",
    v: 36000,
    spec: "1kg",
    kg: 1,
    src: "Kamereo",
    url: "https://www.scribd.com/document/575731136/weekly-HORECA-Kamereo-Price-List-07-03-22-07-03",
    g: "C",
  },
  {
    s: "shiitake",
    n: "Nấm Đông Cô",
    v: 34000,
    spec: "175-200g",
    kg: 0.175,
    src: "Kamereo",
    url: "https://www.scribd.com/document/575731136/weekly-HORECA-Kamereo-Price-List-07-03-22-07-03",
    g: "C",
  },
  {
    s: "wood_ear",
    n: "Nấm Mèo Khô",
    v: 159000,
    spec: "1kg",
    kg: 1,
    src: "Kamereo",
    url: "https://www.scribd.com/document/575731136/weekly-HORECA-Kamereo-Price-List-07-03-22-07-03",
    g: "C",
  },
  {
    s: "wood_ear",
    n: "Mộc Nhĩ Rừng",
    v: 250000,
    spec: "1kg",
    kg: 1,
    src: "Dien Bien Food",
    url: "https://dienbienfoods.com/nam-moc-nhi-rung-tay-bac.html",
    g: "A",
  },
  {
    s: "shiitake",
    n: "Nấm Hương Rừng",
    v: 420000,
    spec: "1kg",
    kg: 1,
    src: "Dien Bien Food",
    url: "https://dienbienfoods.com/nam-moc-nhi-rung-tay-bac.html",
    g: "A",
  },
  ...[
    ["Bulk Kikurage", 2.1],
    ["White Back Fungus", 3],
    ["Wood-Ear Dried", 2],
    ["Wood Ear Fungus", 2.7],
    ["Premium Black Fungus", 1.5],
    ["Cultivated Black Fungus", 2.09],
    ["Frozen Black Fungus", 3.5],
  ].map(([n, v]) => ({
    s: "wood_ear",
    n: String(n),
    v: Number(v),
    spec: "1kg",
    kg: 1,
    src: "Alibaba VN",
    url: vnUrl,
    g: "C",
  })),
].map((x) => ({
  ...x,
  c: "VN",
  cur: x.src === "Alibaba VN" ? "USD" : "VND",
  t: "正常",
  d: x.src === "Kamereo" ? "2022-03-07" : "2026-08-31",
}));
const khBase = [
  {
    s: "shiitake",
    n: "Fresh Shiitake promo",
    v: 2,
    spec: "1 plate",
    src: "Master Gold foodpanda",
    g: "B",
    note: "原价2.50",
  },
  {
    s: "shiitake",
    n: "Fresh Shiitake regular",
    v: 2.5,
    spec: "1 plate",
    src: "Master Gold foodpanda",
    g: "B",
  },
  {
    s: "wood_ear",
    n: "Black Cloud Ear promo",
    v: 2,
    spec: "1 plate",
    src: "Master Gold foodpanda",
    g: "B",
    note: "原价2.50",
  },
  {
    s: "wood_ear",
    n: "Black Cloud Ear regular",
    v: 2.5,
    spec: "1 plate",
    src: "Master Gold foodpanda",
    g: "B",
  },
  {
    s: "oyster_mushroom",
    n: "King Mushroom promo",
    v: 1.76,
    spec: "1 plate",
    src: "Master Gold foodpanda",
    g: "B",
    note: "原价2.20",
  },
  {
    s: "oyster_mushroom",
    n: "King Mushroom regular",
    v: 2.2,
    spec: "1 plate",
    src: "Master Gold foodpanda",
    g: "B",
  },
  {
    s: "shiitake",
    n: "Sliced Dried Shiitake",
    v: 2.5,
    spec: "20g",
    kg: 0.02,
    src: "AEON Mall Plus",
    g: "A",
  },
  {
    s: "oyster_mushroom",
    n: "King Oyster Mushroom Big",
    v: 3.48,
    spec: "300g",
    kg: 0.3,
    src: "AEON foodpanda",
    g: "A",
  },
  {
    s: "shiitake",
    n: "Dried Mushroom",
    v: 5700,
    spec: "50g",
    kg: 0.05,
    src: "AEON Online",
    g: "A",
  },
  {
    s: "shiitake",
    n: "Mushroom set promo",
    v: 6.32,
    spec: "1 set",
    src: "Master Gold foodpanda",
    g: "B",
  },
];
const kh: X[] = khBase.map((x, i) => ({
  ...x,
  c: "KH",
  cur: x.v > 100 ? "KHR" : "USD",
  url: x.src.includes("Master")
    ? "https://www.foodpanda.com.kh/en/restaurant/t5ku/master-gold-tk"
    : x.src.includes("Mall")
      ? "https://aeonmalllogiplus.com.kh/product/tv-sliced-dred-shiitake-mushrooms-20-g/topvalu"
      : x.src.includes("Online")
        ? "https://aeononlineshopping.com/product/aeon1-aeon-phnom-penh/31825"
        : "https://www.foodpanda.com.kh/en/shop/wchz/aeon-sen-sok-supermarket",
  t: x.n.includes("promo") ? "促销" : "正常",
  d: "2026-08-31",
}));
const mm: X[] = [
  {
    s: "oyster_mushroom",
    n: "Mushroom",
    v: 3300,
    spec: "200g",
    kg: 0.2,
    src: "Go Green foodpanda",
    url: "https://www.foodpanda.com.mm/en/shop/s5kk/go-green-myanmar",
    g: "A",
  },
  {
    s: "oyster_mushroom",
    n: "King Oyster Mushroom",
    v: 17500,
    spec: "500g",
    kg: 0.5,
    src: "Makro Myanmar",
    url: "https://www.makropro.com.mm/en/c/fruit-vegetables/vegetables",
    g: "A",
  },
  {
    s: "wood_ear",
    n: "Wood Ear Black Fungus",
    v: 5900,
    spec: "500g",
    kg: 0.5,
    src: "Makro Myanmar",
    url: "https://www.makropro.com.mm/en/c/fruit-vegetables/vegetables",
    g: "A",
  },
  {
    s: "oyster_mushroom",
    n: "King Oyster promo 2023",
    v: 4450,
    spec: "500g",
    kg: 0.5,
    src: "Makro flyer",
    url: "https://www.makromyanmar.com/wp-content/uploads/2023/06/h.pdf",
    g: "D",
  },
  {
    s: "oyster_mushroom",
    n: "King Oyster regular 2023",
    v: 4600,
    spec: "500g",
    kg: 0.5,
    src: "Makro flyer",
    url: "https://www.makromyanmar.com/wp-content/uploads/2023/06/h.pdf",
    g: "D",
  },
  {
    s: "shiitake",
    n: "Dried Shitake",
    v: 38000,
    spec: "未标重量",
    src: "Myanmar menu index",
    url: "https://s3-ap-southeast-1.amazonaws.com/monggo/arena/media/MEDI_FDC69196372646ECB3CD2238396FF580_1574954875.pdf",
    g: "B",
  },
  {
    s: "oyster_mushroom",
    n: "Myanmar mushroom retail low",
    v: 20376.6,
    spec: "1kg",
    kg: 1,
    src: "Selina Wamucii",
    url: "https://www.selinawamucii.com/insights/prices/myanmar/mushrooms-and-truffles/",
    g: "C",
  },
  {
    s: "oyster_mushroom",
    n: "Myanmar mushroom retail high",
    v: 101882.98,
    spec: "1kg",
    kg: 1,
    src: "Selina Wamucii",
    url: "https://www.selinawamucii.com/insights/prices/myanmar/mushrooms-and-truffles/",
    g: "C",
  },
].map((x) => ({
  ...x,
  c: "MM",
  cur: "MMK",
  t: x.g === "D" ? "历史基准" : "正常",
  d: x.g === "D" ? "2023-06-15" : "2026-08-31",
}));
const la: X[] = [...th.slice(0, 5), ...vn.slice(0, 5)].map((x, i) => ({
  ...x,
  c: "LA",
  n: x.n,
  g: "E",
  t: "周边市场价格",
  note: `${x.c === "TH" ? "泰国" : "越南"}市场价格参考`,
  src: x.src,
}));
const rows = [...th, ...vn, ...kh, ...mm, ...la];
const fx: Record<string, number> = {
  THB: 33.159447,
  VND: 26073.33318,
  USD: 1,
  KHR: 4100,
  MMK: 4200,
};
const nm: Record<string, string> = {
  TH: "泰国",
  VN: "越南",
  KH: "柬埔寨",
  MM: "缅甸",
  LA: "老挝",
};
export async function ensureFiveCountryPriceSeed(db: D1Database) {
  const old = await db
    .prepare(
      "SELECT COUNT(*) n FROM products WHERE platform_product_id LIKE 'fc_raw_%'",
    )
    .first<{ n: number }>();
  if (Number(old?.n ?? 0) >= 53)
    return { written: 0, total: rows.length };
  let written = 0,
    failed = 0,
    now = Date.now();
  for (const [i, x] of rows.entries()) {
    const id = `fc_raw_${String(i + 1).padStart(3, "0")}`,
      p = `fc_${i}`,
      cp = `fc_cp_${i}`,
      prod = `${p}:${cp}:${id}`,
      r = fx[x.cur] ?? 1,
      per = x.kg ? x.v / x.kg : null,
      e = JSON.stringify({
        grade: x.g,
        price_type: x.t,
        notes: x.note ?? "",
        raw_pool: true,
      });
    try {
      await db.batch([
        db
          .prepare(
            "INSERT INTO species(id,name_zh,name_en,dictionary_version,review_status) VALUES(?,?,?,?,?) ON CONFLICT(id) DO NOTHING",
          )
          .bind(x.s, x.s, x.s, "raw-v2", "raw"),
        db
          .prepare(
            "INSERT INTO platforms(id,name,country,collection_method,status,updated_at) VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET updated_at=excluded.updated_at",
          )
          .bind(p, x.src, x.c, "raw_pool", "active", now),
        db
          .prepare(
            "INSERT INTO collection_points(id,country,city,platform_id,timezone,active,public_label) VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET active=1",
          )
          .bind(cp, x.c, nm[x.c], p, "UTC", 1, nm[x.c]),
        db
          .prepare(
            "INSERT INTO products(id,platform_id,platform_product_id,collection_point_id,country,city,product_url,original_title,original_description,original_category,species_id,product_form,classification_status,classification_confidence,classification_evidence,first_seen_at,last_seen_at,active) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(platform_id,collection_point_id,platform_product_id) DO UPDATE SET last_seen_at=excluded.last_seen_at",
          )
          .bind(
            prod,
            p,
            id,
            cp,
            x.c,
            nm[x.c],
            x.url,
            x.n,
            x.note ?? null,
            "食用菌",
            x.s,
            x.t === "历史基准"
              ? "historical"
              : x.spec.includes("plate") || x.spec.includes("set")
                ? "prepared_food"
                : "fresh",
            "classified",
            x.g === "A" ? 0.95 : x.g === "B" ? 0.8 : 0.6,
            e,
            now,
            now,
            1,
          ),
        db
          .prepare(
            "INSERT INTO price_observations(id,product_id,observed_at,observation_date,current_price,currency,package_value,package_unit,normalized_quantity_kg,normalized_price_per_kg,price_usd,usd_rate_local_per_usd,fx_source,in_stock,raw_price_text,source_url,source_type,collection_status,validation_status,validation_errors,sanity_outlier,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(product_id,observation_date) DO UPDATE SET current_price=excluded.current_price",
          )
          .bind(
            `${id}:${x.d}`,
            prod,
            new Date(`${x.d}T12:00:00Z`).getTime(),
            x.d,
            x.v,
            x.cur,
            x.kg ?? null,
            x.spec,
            x.kg ?? null,
            per,
            x.v / r,
            r,
            "2026-08-31参考汇率",
            1,
            `${x.v} ${x.cur}`,
            x.url,
            "raw_price_intelligence",
            "collected",
            "valid",
            e,
            0,
            now,
          ),
      ]);
      written++;
    } catch {
      failed++;
    }
  }
  return { written, failed, total: rows.length };
}
