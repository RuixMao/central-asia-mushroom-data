import ProductShell from "../product-shell";
import ReportsClient from "./reports-client";
export default function ReportsPage(){return <ProductShell className="reports-site"><main className="saas-main"><section className="saas-hero compact"><span>YINHENG RESEARCH</span><h1>从新数据到行动建议，不等分析师手工拼表</h1><p>系统汇总最近贸易、价格和物流变化，生成可追溯的中文市场简报；接口不可用时保留已验证基线。</p></section><div className="filter-bar"><b>全部报告</b><a href="/reports/daily">日报</a><a href="/reports/weekly">周报</a><a href="/reports/monthly">月报</a><small>报告内容均经过规则校验</small></div><ReportsClient /></main></ProductShell>}
