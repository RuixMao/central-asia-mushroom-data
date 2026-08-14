# Power BI 数据模型

本文以 `output/powerbi/prices.csv`、`trade.csv`、`logistics.csv` 为主数据源，并以 SQLite 中 `data_snapshots` 的价格缺口记录作为质量监控补充源。所有跨国零售价格比较均使用归一化后的美元/公斤口径。

## 1. 导入前检查

当前仓库已有导出程序 `local/export_powerbi.py`，但交付检查时 `output/powerbi/` 下尚未生成 CSV。首次打开 Power BI Desktop 前，应先执行现有导出流程并确认三个文件均有表头。不要在 Power BI 中手工编造缺失行。

## 2. 表与粒度

### 事实表：零售价格 `事实_零售价格`

粒度：一行代表“某日、某平台、某 SKU 的一次价格观察”。挂牌价不等于成交价。

| 原字段 | 中文标签 | 类型 | 用途 |
|---|---|---:|---|
| country | 国家代码 | 文本 | KZ/UZ/KG/TJ/TM，模型内部键 |
| city | 城市 | 文本 | 零售观察城市 |
| species_zh | 品类 | 文本 | 菌种中文名 |
| original_title | 商品原名 | 文本 | SKU 明细及钻取 |
| product_form | 产品形态代码 | 文本 | fresh/pickled/canned 等 |
| platform_name | 渠道 | 文本 | 零售平台名称 |
| current_price | 当地挂牌价 | 小数 | 仅供本国本币分析 |
| currency | 币种 | 文本 | 当地货币代码 |
| normalized_quantity_kg | 归一化净重（公斤） | 小数 | 规格分析基础 |
| normalized_price_per_kg | 当地币每公斤 | 小数 | 同币种内部比较 |
| price_usd | 每包美元价 | 小数 | 不能直接作为 USD/kg |
| observation_date | 观察日期 | 日期 | 连接日期维度 |
| validation_status | 校验状态 | 文本 | 仅 valid 纳入正式 KPI |

> 重要：当前 CSV 的 `price_usd` 是“每包美元价”，不是“美元/公斤”。在 Power Query 中必须新增 `美元每公斤 = price_usd / normalized_quantity_kg`，且净重为空或不大于 0 时返回 null。

### 事实表：年度贸易 `事实_年度贸易`

粒度：一行代表“某国、某 HS 编码、某年度”的进口统计。

| 原字段 | 中文标签 | 类型 |
|---|---|---:|
| country | 国家代码 | 文本 |
| hs | HS 编码 | 文本 |
| year | 年度 | 整数 |
| value_usd | 进口额（美元） | 小数 |
| net_weight_kg | 净重（公斤） | 小数 |
| unit_price_usd_kg | 进口单价（美元/公斤） | 小数 |

### 事实表：物流时效 `事实_物流时效`

粒度：一行代表“某国、某条线路、某次观察”的物流时效。

| 原字段 | 中文标签 | 类型 |
|---|---|---:|
| country | 国家代码 | 文本 |
| route | 物流线路 | 文本 |
| median_days | 中位时效（天） | 小数 |
| observed_at | 观察时间 | 日期/时间 |

### 补充事实表：数据缺口 `事实_数据缺口`

来源：SQLite `data_snapshots`，仅筛选 `metric='price_retail'` 且 JSON 中 `status='gap'`。建议在 Power Query 中展开：`country`、`source`、`captured_at`、`reason`、`status`。粒度为“一次来源缺口记录”。没有 gap 行不等于缺口为 0，仍须有来源计划表作为分母。

### 维度表

| 表 | 主键 | 建议字段 |
|---|---|---|
| `维度_日期` | 日期 | 年、季度、月份、年月、周、是否今日 |
| `维度_国家` | 国家代码 | 国家中文全称、排序 |
| `维度_品类` | 品类 | 品类排序 |
| `维度_形态` | 产品形态代码 | 产品形态中文 |
| `维度_渠道` | 渠道 | 渠道名称 |
| `维度_HS` | HS 编码 | HS 编码、口径说明 |

国家映射固定为：KZ=哈萨克斯坦、UZ=乌兹别克斯坦、KG=吉尔吉斯斯坦、TJ=塔吉克斯坦、TM=土库曼斯坦。形态建议映射：fresh=鲜品、pickled=腌渍、canned=罐藏；其他值显示“待归类”，不强行归并。

## 3. 关系

采用星型模型，筛选方向均为“维度表到事实表”的单向筛选：

- `维度_日期[日期]` 1:* `事实_零售价格[观察日期]`
- `维度_日期[日期]` 1:* `事实_物流时效[观察日期]`
- `维度_国家[国家代码]` 1:* 三张事实表及缺口表的国家代码
- `维度_品类[品类]` 1:* `事实_零售价格[品类]`
- `维度_形态[产品形态代码]` 1:* `事实_零售价格[产品形态代码]`
- `维度_渠道[渠道]` 1:* `事实_零售价格[渠道]`
- `维度_HS[HS 编码]` 1:* `事实_年度贸易[HS 编码]`

不要直接连接零售价格与年度贸易。两者仅共享国家维度，零售挂牌价与海关进口单价必须分开显示。

## 4. Power Query 清洗

在 `事实_零售价格` 中新增：

```powerquery
国家中文 = Record.FieldOrDefault(
    [KZ="哈萨克斯坦", UZ="乌兹别克斯坦", KG="吉尔吉斯斯坦", TJ="塔吉克斯坦", TM="土库曼斯坦"],
    [country], "未知国家")

美元每公斤 = if [price_usd] = null or [normalized_quantity_kg] = null
    or [normalized_quantity_kg] <= 0
    then null
    else [price_usd] / [normalized_quantity_kg]

规格组 = if [normalized_quantity_kg] = null then "规格未知"
    else if Number.Abs([normalized_quantity_kg] - 0.3) <= 0.03 then "300g"
    else if Number.Abs([normalized_quantity_kg] - 1.0) <= 0.05 then "1kg"
    else "其他规格"
```

同时执行：

1. 将日期字段转换为日期类型，年度转换为整数。
2. 将价格、重量、贸易额和天数转换为小数。
3. 把空值保留为 null，不转换为 0。
4. 正式指标只筛选 `validation_status="valid"`。
5. 对 `country + city + original_title + platform_name + observation_date` 检查重复，但不要无依据删除同日不同规格商品。

## 5. 建模边界

- `prices.csv` 没有稳定 SKU ID，钻取可显示商品原名，但不能可靠地跨日追踪同一 SKU。
- `prices.csv` 没有促销价和库存字段，因此促销占比、缺货率不能由该 CSV 准确计算。
- `trade.csv` 是年度粒度，不能用日期日历做日/月级环比。
- `logistics.csv` 只有中位时效，无法还原分位数或波动范围。

