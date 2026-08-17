export type CountryCode = "ALL" | "KZ" | "UZ" | "KG" | "TJ" | "TM";

export type TradeRecord = {
  countryCode: Exclude<CountryCode, "ALL">;
  country: string;
  hs: string;
  product: string;
  y2022: number | null;
  y2023: number | null;
  y2024: number | null;
  quantity2024Tonnes?: number;
};

export type MirrorRecord = {
  countryCode: Exclude<CountryCode, "ALL">;
  country: string;
  hs: string;
  product: string;
  importerCifUsd: number | null;
  chinaFobUsd: number | null;
  officialQuantityKg?: number;
  confirmedTradeUsd?: number;
  confirmedQuantityKg?: number;
  confirmedPartners?: string[];
  confidence: "A+" | "A" | "B+" | "B";
  confidenceBasis: string;
};

export type Opportunity = {
  id: string;
  countryCode: Exclude<CountryCode, "ALL">;
  country: string;
  hs: string;
  product: string;
  score: number;
  coverage: number;
  confidence: "A" | "A−" | "B+" | "B";
  status: "优先验证" | "值得跟进" | "补数观察" | "暂缓";
  marketUsd: number;
  change: number;
  signal: string;
  nextAction: string;
  metrics: { label: string; value: number | null; note: string }[];
};

export const countryOptions: { code: CountryCode; label: string; short: string }[] = [
  { code: "ALL", label: "中亚五国", short: "全部" },
  { code: "KZ", label: "哈萨克斯坦", short: "哈萨克斯坦" },
  { code: "UZ", label: "乌兹别克斯坦", short: "乌兹别克斯坦" },
  { code: "KG", label: "吉尔吉斯斯坦", short: "吉尔吉斯斯坦" },
  { code: "TJ", label: "塔吉克斯坦", short: "塔吉克斯坦" },
  { code: "TM", label: "土库曼斯坦", short: "土库曼斯坦" },
];

export const countrySummaries = [
  { code: "KZ" as const, country: "哈萨克斯坦", value: 5_630_457, share: 80.9, change: 7.2, state: "核心市场" },
  { code: "KG" as const, country: "吉尔吉斯斯坦", value: 805_134, share: 11.6, change: 93.0, state: "高速增长" },
  { code: "UZ" as const, country: "乌兹别克斯坦", value: 525_008, share: 7.5, change: -12.5, state: "结构调整" },
  { code: "TJ" as const, country: "塔吉克斯坦", value: null, share: 0, change: null, state: "待补报" },
  { code: "TM" as const, country: "土库曼斯坦", value: null, share: 0, change: null, state: "待补报" },
];

export const tradeRecords: TradeRecord[] = [
  { countryCode: "KZ", country: "哈萨克斯坦", hs: "070951", product: "鲜/冷双孢蘑菇", y2022: 8_893_873, y2023: 3_181_278, y2024: 4_193_266, quantity2024Tonnes: 3_489 },
  { countryCode: "KZ", country: "哈萨克斯坦", hs: "200310", product: "加工保藏蘑菇", y2022: 4_412_358, y2023: 1_644_872, y2024: 1_027_970 },
  { countryCode: "KZ", country: "哈萨克斯坦", hs: "070959", product: "其他鲜蘑菇", y2022: 510_974, y2023: 426_093, y2024: 409_221 },
  { countryCode: "UZ", country: "乌兹别克斯坦", hs: "070951", product: "鲜/冷双孢蘑菇", y2022: 15_930, y2023: 488_375, y2024: 456_804 },
  { countryCode: "UZ", country: "乌兹别克斯坦", hs: "200310", product: "加工保藏蘑菇", y2022: 69_233, y2023: 111_800, y2024: 68_204 },
  { countryCode: "KG", country: "吉尔吉斯斯坦", hs: "070951", product: "鲜/冷双孢蘑菇", y2022: 9_994, y2023: 40_966, y2024: 40_376, quantity2024Tonnes: 24 },
  { countryCode: "KG", country: "吉尔吉斯斯坦", hs: "070959", product: "其他鲜蘑菇", y2022: 97_554, y2023: 246_088, y2024: 535_916 },
  { countryCode: "KG", country: "吉尔吉斯斯坦", hs: "200310", product: "加工保藏蘑菇", y2022: 130_482, y2023: 130_030, y2024: 228_842, quantity2024Tonnes: 46 },
  { countryCode: "TJ", country: "塔吉克斯坦", hs: "200310", product: "加工保藏蘑菇", y2022: 39_358, y2023: 119_104, y2024: null },
];

export const mirrorRecords: MirrorRecord[] = [
  { countryCode: "KZ", country: "哈萨克斯坦", hs: "070951", product: "鲜或冷藏蘑菇", importerCifUsd: 4_647_430, chinaFobUsd: 498_280, officialQuantityKg: 4_015_820, confidence: "A+", confidenceBasis: "进口国完整申报，含数量与来源国" },
  { countryCode: "KZ", country: "哈萨克斯坦", hs: "200310", product: "加工保藏蘑菇", importerCifUsd: 1_353_310, chinaFobUsd: 1_099_830, officialQuantityKg: 1_627_780, confidence: "A+", confidenceBasis: "进口国完整申报，含数量与来源国" },
  { countryCode: "UZ", country: "乌兹别克斯坦", hs: "070951", product: "鲜或冷藏蘑菇", importerCifUsd: 456_800, chinaFobUsd: null, officialQuantityKg: 197_396, confidence: "A+", confidenceBasis: "进口国完整申报，含数量与来源国" },
  { countryCode: "UZ", country: "乌兹别克斯坦", hs: "200310", product: "加工保藏蘑菇", importerCifUsd: 70_810, chinaFobUsd: 10_400, officialQuantityKg: 20_080, confidence: "A+", confidenceBasis: "进口国完整申报，含数量与来源国" },
  { countryCode: "KG", country: "吉尔吉斯斯坦", hs: "070951", product: "鲜或冷藏蘑菇", importerCifUsd: 288_150, chinaFobUsd: 288_150, officialQuantityKg: 135_714, confidence: "A+", confidenceBasis: "进口国完整申报，含数量与来源国" },
  { countryCode: "KG", country: "吉尔吉斯斯坦", hs: "200310", product: "加工保藏蘑菇", importerCifUsd: 115_930, chinaFobUsd: 70_190, officialQuantityKg: 112_704, confidence: "A+", confidenceBasis: "进口国完整申报，含数量与来源国" },
  { countryCode: "TJ", country: "塔吉克斯坦", hs: "200310", product: "加工保藏蘑菇", importerCifUsd: null, chinaFobUsd: 278_116, confirmedTradeUsd: 286_590, confirmedQuantityKg: 263_264, confirmedPartners: ["中国", "哈萨克斯坦"], confidence: "B+", confidenceBasis: "两国对塔出口申报汇总" },
  { countryCode: "TM", country: "土库曼斯坦", hs: "200310", product: "加工保藏蘑菇", importerCifUsd: null, chinaFobUsd: 230_076, confirmedTradeUsd: 249_690, confirmedQuantityKg: 127_563, confirmedPartners: ["中国", "土耳其", "亚美尼亚"], confidence: "B+", confidenceBasis: "三国对土出口申报汇总" },
];

export const opportunities: Opportunity[] = [
  {
    id: "kz-070951",
    countryCode: "KZ",
    country: "哈萨克斯坦",
    hs: "070951",
    product: "鲜/冷双孢蘑菇",
    score: 76,
    coverage: 75,
    confidence: "A−",
    status: "值得跟进",
    marketUsd: 4_193_266,
    change: 31.8,
    signal: "进口依赖粗估约87%，本地零售价格带稳定，适合验证冷链到岸成本。",
    nextAction: "向阿拉木图3家渠道获取同规格周度成交价，并核算喀什冷链线路。",
    metrics: [
      { label: "市场规模", value: 84, note: "2024年进口额419万美元" },
      { label: "增长动能", value: 44, note: "较2023年反弹31.8%，两年趋势仍偏弱" },
      { label: "进口依赖", value: 87, note: "进口量与FAO全品类产量粗估，口径置信度受限" },
      { label: "渠道可达", value: 100, note: "已观察到5个独立零售/批发渠道" },
    ],
  },
  {
    id: "kg-070959",
    countryCode: "KG",
    country: "吉尔吉斯斯坦",
    hs: "070959",
    product: "其他鲜蘑菇",
    score: 70,
    coverage: 45,
    confidence: "B",
    status: "补数观察",
    marketUsd: 535_916,
    change: 117.8,
    signal: "2024年进口额同比翻倍，两年增长449%，但缺少来源国和当地价格证据。",
    nextAction: "补采比什凯克批发市场价格、来源国结构和月度进口节奏。",
    metrics: [
      { label: "市场规模", value: 46, note: "2024年进口额53.6万美元" },
      { label: "增长动能", value: 100, note: "同比增长117.8%，触发高增长信号" },
      { label: "进口依赖", value: null, note: "缺少同口径本地产量" },
      { label: "渠道可达", value: null, note: "尚未核验活跃采购渠道" },
    ],
  },
  {
    id: "uz-070951",
    countryCode: "UZ",
    country: "乌兹别克斯坦",
    hs: "070951",
    product: "鲜/冷双孢蘑菇",
    score: 64,
    coverage: 55,
    confidence: "B+",
    status: "补数观察",
    marketUsd: 456_804,
    change: -6.5,
    signal: "相比2022年仍处于高位，塔什干零售挂牌价约6万–7.8万苏姆/kg。",
    nextAction: "补齐净重、批发成交价和进口来源国，验证高零售价是否可转化为毛利。",
    metrics: [
      { label: "市场规模", value: 44, note: "2024年进口额45.7万美元" },
      { label: "增长动能", value: 77, note: "低基数高速增长，最近一年回落6.5%" },
      { label: "价差空间", value: 55, note: "仅有零售挂牌价，证据置信度封顶" },
      { label: "渠道可达", value: 85, note: "观察到电商、商超等4类渠道" },
    ],
  },
  {
    id: "kg-200310",
    countryCode: "KG",
    country: "吉尔吉斯斯坦",
    hs: "200310",
    product: "加工保藏蘑菇",
    score: 58,
    coverage: 45,
    confidence: "B",
    status: "补数观察",
    marketUsd: 228_842,
    change: 76.0,
    signal: "进口增长明显，但中吉两侧镜像差异71.9%，暂不计算中国份额。",
    nextAction: "先核对HS版本、贸易方向和转口路径，再开展渠道报价。",
    metrics: [
      { label: "市场规模", value: 32, note: "2024年进口额22.9万美元" },
      { label: "增长动能", value: 90, note: "同比增长76%" },
      { label: "中国拓展", value: null, note: "镜像异常，暂停使用" },
      { label: "渠道可达", value: null, note: "缺少核验渠道" },
    ],
  },
  {
    id: "kz-200310",
    countryCode: "KZ",
    country: "哈萨克斯坦",
    hs: "200310",
    product: "加工保藏蘑菇",
    score: 34,
    coverage: 45,
    confidence: "A−",
    status: "暂缓",
    marketUsd: 1_027_970,
    change: -37.5,
    signal: "市场连续收缩且镜像差异72.1%，优先查明口径而非扩大投入。",
    nextAction: "复核中哈贸易口径、转口链路及CIF/FOB差异，暂不进入机会榜。",
    metrics: [
      { label: "市场规模", value: 58, note: "2024年进口额103万美元" },
      { label: "增长动能", value: 5, note: "同比下降37.5%，两年下降76.7%" },
      { label: "中国拓展", value: null, note: "镜像异常，暂停使用" },
      { label: "渠道可达", value: null, note: "加工品渠道尚未核验" },
    ],
  },
];

export const priceObservations = [
  { countryCode: "KZ" as const, city: "阿拉木图", channel: "电商/商超", product: "鲜双孢菇", price: "2,730–3,300 ₸/kg", date: "2026-08", source: "Arbuz / Carefood" },
  { countryCode: "KZ" as const, city: "阿拉木图", channel: "高端电商", product: "Freedom Fresh双孢菇", price: "6,930 ₸/kg", date: "2026-08", source: "Arbuz" },
  { countryCode: "KZ" as const, city: "阿拉木图", channel: "小批发", product: "鲜双孢菇", price: "2,600 ₸/kg", date: "2026-08", source: "Optoffka" },
  { countryCode: "KZ" as const, city: "阿拉木图", channel: "批发", product: "鲜平菇", price: "1,300–1,500 ₸/kg", date: "2026-08", source: "Flagma" },
  { countryCode: "KZ" as const, city: "阿拉木图", channel: "零售", product: "鲜平菇", price: "2,095–3,000 ₸/kg", date: "2026-08", source: "Carefood / Optoffka" },
  { countryCode: "UZ" as const, city: "塔什干", channel: "电商/零售", product: "鲜双孢菇", price: "60,000–78,000 сум/kg", date: "2026-07~08", source: "OLX / Tegen / Prom" },
  { countryCode: "UZ" as const, city: "塔什干", channel: "电商平台", product: "腌制双孢菇430ml", price: "25,990 сум/罐", date: "2026-08", source: "Uzum Market" },
];

export const dataSources = [
  { name: "UN Comtrade", level: "A", scope: "五国贸易主表", cadence: "年/月", status: "已接入基线", note: "官方贸易统计；保留报告国、伙伴国、贸易流向和HS版本。", url: "https://comtradeapi.un.org" },
  { name: "中国海关", level: "A", scope: "中国出口镜像", cadence: "月", status: "待自动接入", note: "用于核对中国对中亚出口、贸易方式和境内地区。", url: "https://english.customs.gov.cn/Statistics/Statistics" },
  { name: "FAOSTAT", level: "A−", scope: "农业供给能力", cadence: "年", status: "已接入基线", note: "中亚菌类产量为FAO估算值；衍生指标需标注口径限制。", url: "https://www.fao.org/faostat" },
  { name: "哈萨克斯坦统计局", level: "A", scope: "4/6/10位商品", cadence: "月", status: "排期接入", note: "可补充国别—商品、地区贸易和EAEU互贸明细。", url: "https://stat.gov.kz/en/industries/economy/foreign-market/" },
  { name: "乌兹别克斯坦统计委", level: "A", scope: "外贸与经济指标", cadence: "月/年", status: "排期接入", note: "官方页面提供CSV、JSON和XML数据出口。", url: "https://stat.uz/en/official-statistics/merchandise-trade" },
  { name: "市场观察池", level: "B+", scope: "价格与渠道", cadence: "周", status: "7条已核验", note: "挂牌价不是成交价；每条记录绑定采集日期、来源与证据。", url: "#prices" },
];

