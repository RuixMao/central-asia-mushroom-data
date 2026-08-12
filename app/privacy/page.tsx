import Link from "next/link";
import ProductShell from "../product-shell";
export default function Privacy(){return <ProductShell><main className="legal-page"><Link href="/">← 返回首页</Link><h1>隐私政策</h1><p>本网站当前为产品展示与需求沟通入口。我们仅在您主动提交表单时收集姓名、机构、邮箱及需求描述，用于回复咨询和改进服务。</p><p>在正式联系方式和数据处理流程上线前，演示表单不会向外部系统发送数据。正式版本将进一步说明数据保存期限、使用范围与用户权利。</p></main></ProductShell>}
