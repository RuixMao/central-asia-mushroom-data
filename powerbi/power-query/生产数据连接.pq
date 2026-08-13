// 在 Power Query 新建“空白查询”，分别复制函数和六个查询。
let
    站点地址 = "https://yinheng-central-asia-intel.mrxkk.chatgpt.site",
    获取数据 = (表名 as text) as table =>
        let
            来源 = Json.Document(Web.Contents(站点地址, [RelativePath="api/powerbi", Query=[table=表名, format="json"]])),
            行 = 来源[records],
            结果 = if List.Count(行)=0 then #table({}, {}) else Table.FromRecords(行)
        in 结果
in
    获取数据

// 查询名：价格明细
// = 获取数据("prices")
// 查询名：每日汇总
// = 获取数据("daily")
// 查询名：采集运行
// = 获取数据("runs")
// 查询名：采集错误
// = 获取数据("errors")
// 查询名：商品
// = 获取数据("products")
// 查询名：菌种
// = 获取数据("species")
