# Power BI DAX 度量库

以下公式假定表名已按 `data-model.md` 设置。所有 gap 和缺失历史均返回 `BLANK()`，不得用 0 代替。

## 1. 总览驾驶舱

```dax
今日日期 = MAX('事实_零售价格'[观察日期])

今日有效价格条数 =
VAR d = [今日日期]
RETURN CALCULATE(
    COUNTROWS('事实_零售价格'),
    '事实_零售价格'[观察日期] = d,
    '事实_零售价格'[校验状态] = "valid",
    NOT ISBLANK('事实_零售价格'[美元每公斤])
)

覆盖国家数 =
CALCULATE(
    DISTINCTCOUNT('事实_零售价格'[国家代码]),
    '事实_零售价格'[校验状态] = "valid"
)

五国均价（美元/公斤） =
CALCULATE(
    MEDIAN('事实_零售价格'[美元每公斤]),
    '事实_零售价格'[校验状态] = "valid"
)

双孢菇均价（美元/公斤） =
CALCULATE([五国均价（美元/公斤）], '事实_零售价格'[品类] = "双孢菇")

物流平均时效（天） = AVERAGE('事实_物流时效'[中位时效（天）])

最新数据距今天数 = DATEDIFF([今日日期], TODAY(), DAY)
```

`五国均价` 使用 SKU 级“美元每公斤”的中位数，避免极端挂牌价拉高均值。

## 2. 数据质量

如果另有一张 `维度_计划来源`，每行代表每天应采集的一个国家×渠道来源，则使用：

```dax
今日总源数 =
VAR d = [今日日期]
RETURN CALCULATE(COUNTROWS('维度_计划来源'), '维度_计划来源'[启用日期] <= d)

今日有效源数 =
VAR d = [今日日期]
RETURN CALCULATE(
    DISTINCTCOUNT('事实_零售价格'[来源键]),
    '事实_零售价格'[观察日期] = d,
    '事实_零售价格'[校验状态] = "valid"
)

源有效率 = DIVIDE([今日有效源数], [今日总源数])
数据缺口率 = IF(ISBLANK([源有效率]), BLANK(), 1 - [源有效率])
```

当前 CSV 没有 `来源键` 和计划来源分母，所以不要直接启用以上度量。可先展示：

```dax
缺口记录数 = COUNTROWS('事实_数据缺口')

有效记录占比 =
DIVIDE(
    CALCULATE(COUNTROWS('事实_零售价格'), '事实_零售价格'[校验状态] = "valid"),
    COUNTROWS('事实_零售价格')
)

异常价格数 =
CALCULATE(
    COUNTROWS('事实_零售价格'),
    '事实_零售价格'[校验状态] <> "valid"
)
```

## 3. 价格变化与价差

```dax
前一有效日均价 =
VAR currentDate = MAX('维度_日期'[日期])
VAR previousDate =
    MAXX(
        FILTER(ALL('维度_日期'[日期]), '维度_日期'[日期] < currentDate),
        '维度_日期'[日期]
    )
VAR historyDays =
    CALCULATE(DISTINCTCOUNT('事实_零售价格'[观察日期]), ALL('维度_日期'))
RETURN IF(historyDays < 3 || ISBLANK(previousDate), BLANK(),
    CALCULATE([五国均价（美元/公斤）], '维度_日期'[日期] = previousDate))

零售环比 =
VAR previousValue = [前一有效日均价]
RETURN IF(ISBLANK(previousValue), BLANK(),
    DIVIDE([五国均价（美元/公斤）] - previousValue, previousValue))

零售同比 =
VAR historyDays = CALCULATE(DISTINCTCOUNT('事实_零售价格'[观察日期]), ALL('维度_日期'))
VAR lastYearValue = CALCULATE([五国均价（美元/公斤）], DATEADD('维度_日期'[日期], -1, YEAR))
RETURN IF(historyDays < 3 || ISBLANK(lastYearValue), BLANK(),
    DIVIDE([五国均价（美元/公斤）] - lastYearValue, lastYearValue))

鲜品中位价 = CALCULATE([五国均价（美元/公斤）], '维度_形态'[产品形态代码] = "fresh")
腌渍中位价 = CALCULATE([五国均价（美元/公斤）], '维度_形态'[产品形态代码] = "pickled")
形态价差 = IF(ISBLANK([鲜品中位价]) || ISBLANK([腌渍中位价]), BLANK(), [鲜品中位价] - [腌渍中位价])

300g中位价 = CALCULATE([五国均价（美元/公斤）], '事实_零售价格'[规格组] = "300g")
1kg中位价 = CALCULATE([五国均价（美元/公斤）], '事实_零售价格'[规格组] = "1kg")
规格价差 = IF(ISBLANK([300g中位价]) || ISBLANK([1kg中位价]), BLANK(), [300g中位价] - [1kg中位价])

国家价格排名 =
RANKX(ALLSELECTED('维度_国家'[国家中文全称]), [五国均价（美元/公斤）], , ASC, DENSE)

价格洼地 = IF([国家价格排名] = 1, "价格洼地", BLANK())
价格高地排名 =
RANKX(ALLSELECTED('维度_国家'[国家中文全称]), [五国均价（美元/公斤）], , DESC, DENSE)
```

## 4. 贸易趋势

```dax
年度进口额（美元） = SUM('事实_年度贸易'[进口额（美元）])
年度进口量（公斤） = SUM('事实_年度贸易'[净重（公斤）])

加权进口单价（美元/公斤） =
DIVIDE([年度进口额（美元）], [年度进口量（公斤）])

进口额同比 =
VAR y = MAX('事实_年度贸易'[年度])
VAR previousValue = CALCULATE([年度进口额（美元）], FILTER(ALL('事实_年度贸易'[年度]), '事实_年度贸易'[年度] = y - 1))
RETURN IF(ISBLANK(previousValue), BLANK(), DIVIDE([年度进口额（美元）] - previousValue, previousValue))

进口单价同比 =
VAR y = MAX('事实_年度贸易'[年度])
VAR previousValue = CALCULATE([加权进口单价（美元/公斤）], FILTER(ALL('事实_年度贸易'[年度]), '事实_年度贸易'[年度] = y - 1))
RETURN IF(ISBLANK(previousValue), BLANK(), DIVIDE([加权进口单价（美元/公斤）] - previousValue, previousValue))
```

## 5. 物流与决策支持

```dax
线路中位时效（天） = MEDIAN('事实_物流时效'[中位时效（天）])
最快线路时效（天） = MIN('事实_物流时效'[中位时效（天）])
最慢线路时效（天） = MAX('事实_物流时效'[中位时效（天）])
线路时效差（天） = [最慢线路时效（天）] - [最快线路时效（天）]

情景采购成本（美元/公斤） =
[五国均价（美元/公斤）] * (1 + SELECTEDVALUE('参数_价格变动'[参数_价格变动 值], 0))

数据新鲜度状态 =
SWITCH(TRUE(), [最新数据距今天数] <= 1, "新鲜", [最新数据距今天数] <= 3, "注意", "过期")

数据新鲜度颜色 =
SWITCH([数据新鲜度状态], "新鲜", "#22C55E", "注意", "#F59E0B", "#EF4444")
```

格式：美元/公斤 `$#,0.00`；百分比 `0.0%`；天数 `0.0`。零售和贸易度量不要放在同一数值轴上。

