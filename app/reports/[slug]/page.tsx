import ProductShell from "../../product-shell";
import ReportDetailClient from "./report-detail-client";

export default async function ReportDetailPage({params}:{params:Promise<{slug:string}>}){
  const rawSlug=(await params).slug;
  const slug=(()=>{try{return decodeURIComponent(rawSlug)}catch{return rawSlug}})();
  return <ProductShell className="reports-site"><main className="saas-main report-detail-page"><ReportDetailClient slug={slug}/></main></ProductShell>;
}
