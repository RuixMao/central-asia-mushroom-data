import ProductShell from "../../product-shell";
import ReportsClient from "../reports-client";
export default function Page(){return <ProductShell className="reports-site"><main className="saas-main"><section className="saas-hero compact"><span>ANNUAL RESEARCH</span><h1>年度市场报告</h1><p>复盘全年市场表现，评估市场规模、竞争格局与五年发展情景。</p></section><div className="filter-bar"><a href="/reports">全部</a><a href="/reports/daily">日报</a><a href="/reports/weekly">周报</a><a href="/reports/monthly">月报</a><a href="/reports/quarterly">季报</a><b>年报</b></div><ReportsClient filter="annual"/></main></ProductShell>}
