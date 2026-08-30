import ProductShell from "../product-shell";
export default function Docs(){return <ProductShell><main className="docs-layout"><aside><b>API 文档</b><a href="#auth">认证</a><a href="#trade">贸易数据</a><a href="#limits">限流</a><a href="#errors">错误码</a></aside><article><span>REST API / V1</span><h1>把菌业出海数据接入你的系统</h1><p>所有请求使用 HTTPS，并以 JSON 返回。日期采用 ISO 8601，金额默认以美元计价。</p><h2 id="auth">认证</h2><p>在账户后台获取 API Key，并通过 Bearer Token 发送。</p><pre><code>{`curl "https://api.yinheng.tech/v1/trade?country=KZ&hs=070951" \\
  -H "Authorization: Bearer YOUR_API_KEY"`}</code></pre><h2 id="trade">GET /api/v1/trade</h2><div className="param-table"><b>参数</b><b>类型</b><b>说明</b><span>country</span><span>string</span><span>KZ / UZ / KG / TJ / TM / LA / VN / TH / MM / KH</span><span>hs</span><span>string</span><span>6 位 HS 编码</span><span>start</span><span>string</span><span>起始统计期 YYYY-MM</span></div><pre><code>{`{
  "data": [{
    "period": "2024",
    "country": "KZ",
    "hs": "070951",
    "trade_value_usd": 4193266,
    "net_weight_kg": 3489000
  }],
  "meta": { "source": "UN Comtrade", "count": 1 }
}`}</code></pre><h2 id="limits">限流</h2><p>免费版每月 10 次，专业版每月 1,000 次；同一 Key 每秒最多 5 次请求。超限返回 429。</p><h2 id="errors">错误码</h2><p>401 表示 Key 缺失或无效；403 表示当前套餐无权访问；429 表示达到频率或月度配额。</p></article></main></ProductShell>}
