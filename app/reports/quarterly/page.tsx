import ProductShell from "../../product-shell";
import ReportsClient from "../reports-client";
export default function Page(){return <ProductShell className="reports-site"><main className="saas-main"><section className="saas-hero compact"><span>QUARTERLY RESEARCH</span><h1>季度市场报告</h1><p>分析竞争、渠道与成本格局，为下一季度市场布局提供依据。</p></section><div className="filter-bar"><a href="/reports">全部</a><a href="/reports/daily">日报</a><a href="/reports/weekly">周报</a><a href="/reports/monthly">月报</a><b>季报</b><a href="/reports/annual">年报</a></div><ReportsClient filter="quarterly"/></main></ProductShell>}
