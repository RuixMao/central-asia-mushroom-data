export const datasets = [
  { slug: "central-asia-mushroom-trade", name: "中亚五国菌类进口贸易", category: "贸易", frequency: "每月", countries: "中亚五国", records: "18,420", updated: "2026-08-10", value: "判断市场规模、增速、来源国与品类结构", source: "UN Comtrade", fields: ["统计期", "报告国", "伙伴国", "HS 编码", "贸易额（USD）", "净重（kg）"] },
  { slug: "retail-price-monitor", name: "重点城市终端价格监测", category: "价格", frequency: "每周", countries: "4 国 7 城", records: "3,680", updated: "2026-08-11", value: "跟踪零售价格带、渠道差异与异常波动", source: "公开零售与电商渠道", fields: ["日期", "国家", "城市", "产品", "规格", "本币价格", "来源"] },
  { slug: "cold-chain-logistics", name: "中国—中亚冷链物流时效", category: "物流", frequency: "每周", countries: "6 条核心线路", records: "1,245", updated: "2026-08-11", value: "测算到岸时间、通关波动和履约风险", source: "物流企业公开报价与线路公告", fields: ["起点", "终点", "运输方式", "时效下限", "时效上限", "来源数"] },
  { slug: "buyer-directory", name: "中亚菌类进口商与渠道名录", category: "企业", frequency: "每月", countries: "中亚五国", records: "860", updated: "2026-08-01", value: "发现潜在买家、经销渠道和合作伙伴", source: "海关记录与公开工商信息", fields: ["企业", "国家", "城市", "角色", "品类", "活跃度"] },
  { slug: "market-access-standards", name: "菌类准入标准与标签要求", category: "标准", frequency: "按变更", countries: "中亚五国", records: "126", updated: "2026-07-28", value: "降低合规返工与清关不确定性", source: "政府与标准机构", fields: ["国家", "法规", "适用品类", "要求", "生效日", "原文链接"] },
  { slug: "market-opportunity-score", name: "国别×品类机会评分", category: "分析", frequency: "每月", countries: "15 个市场单元", records: "540", updated: "2026-08-10", value: "快速排序值得验证的出口机会", source: "因恒科技衍生模型", fields: ["国家", "HS 编码", "市场规模", "增速", "证据覆盖", "机会分"] },
];

export const sampleRows = [
  ["2024", "哈萨克斯坦", "070951", "鲜/冷双孢蘑菇", "$4,193,266", "3,489 吨"],
  ["2024", "哈萨克斯坦", "200310", "加工保藏蘑菇", "$1,027,970", "待补"],
  ["2024", "吉尔吉斯斯坦", "070959", "其他鲜蘑菇", "$535,916", "待补"],
  ["2024", "乌兹别克斯坦", "070951", "鲜/冷双孢蘑菇", "$456,804", "197 吨"],
  ["2024", "吉尔吉斯斯坦", "200310", "加工保藏蘑菇", "$228,842", "46 吨"],
];

export const reports = [
  { type: "每日简报", country: "中亚五国", date: "2026-08-11", title: "哈萨克市场企稳，吉尔吉斯其他鲜菇进口加速", summary: "哈萨克斯坦仍占中亚已报告菌类进口额的八成以上；吉尔吉斯斯坦其他鲜菇保持高增长，但公开渠道与来源国信息仍较有限。" },
  { type: "周报", country: "哈萨克斯坦", date: "2026-08-08", title: "阿拉木图鲜菇价格带与冷链到岸机会", summary: "主流电商与商超鲜双孢菇挂牌价集中在 2,730–3,300 坚戈/公斤，建议先以同规格周度成交价验证渠道毛利。" },
  { type: "专题", country: "中亚五国", date: "2026-08-01", title: "2026 中亚菌类出口机会地图", summary: "以市场规模、增长动能、进口依赖、渠道可达和证据完整度五个维度，筛选 15 个国别品类组合。" },
];
