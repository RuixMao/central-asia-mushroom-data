import SiteNav from "../site-nav";
import MarketingFooter from "../marketing-footer";

const available = [
  ["官方贸易", "UN Comtrade、中国出口镜像", "国家/伙伴/流向/HS/金额/数量/年份", "市场规模、增长趋势、镜像核验"],
  ["农业供给", "FAOSTAT、中国供给资源", "国家/品类/产量/年份/估算标识", "供需粗估、品类筛选"],
  ["市场价格", "电商、商超、批发挂牌", "城市/渠道/产品/规格/币种/日期/来源", "价格带、渠道地图、周报"],
  ["市场信号", "行业媒体、访谈与公开资料", "事件/主体/市场/日期/证据等级", "市场摘要、机会提示"],
];

const differentiated = [
  ["真实成交数据库", "成交价、采购量、规格、账期、频次", "合作商回传 + 定向调研", "价格指数、采购基准", "成交基准"],
  ["进口商与买家图谱", "企业、联系人、品类、采购周期、信用", "工商数据 + 展会 + 渠道验证", "买家库、销售线索订阅", "渠道洞察"],
  ["喀什—中亚物流指数", "线路、报价、时效、冷链损耗、通关异常", "货代/口岸/承运商周度采集", "物流成本指数、线路 API", "跨境履约"],
  ["项目与投资数据库", "园区、项目、产能、资金需求、进度、合作方", "政府公开信息 + 在地跟踪", "项目库、投资机会订阅", "项目研判"],
  ["政策与合规知识库", "关税、检疫、准入、补贴、政策变化", "法规监测 + 专家复核", "合规提醒、品类准入包", "合规支持"],
  ["农业供需预测集", "月度消费、库存、产地、天气、季节性", "多源建模 + 持续校准", "预测模型、行业指数", "趋势预测"],
];

export default function AssetsPage(){
  return <div className="marketing-site">
    <SiteNav/>
    <main className="subpage data-assets-page">
      <section className="subhero">
        <span>DATA ASSETS</span>
        <h1>把分散市场信息，转化为可用决策依据</h1>
        <p>整合贸易、供给、价格与市场信号，以统一口径和可追溯来源，帮助客户判断市场、筛选机会并降低决策成本。</p>
      </section>

      <section className="asset-section">
        <div className="landing-heading"><span>AVAILABLE NOW</span><h2>现有数据基础</h2><p>覆盖市场研判所需的核心公开数据，并持续更新来源、口径与证据等级。</p></div>
        <div className="data-table">
          <div className="data-table-head"><span>数据域</span><span>来源</span><span>核心字段</span><span>客户用途</span></div>
          {available.map(row=><div className="data-table-row" key={row[0]}>{row.map((cell,i)=><span key={cell} className={i===0?"cell-title":""}>{cell}</span>)}</div>)}
        </div>
      </section>

      <section className="asset-section asset-future-section">
        <div className="landing-heading">
          <span>DIFFERENTIATED DATA</span>
          <h2>更接近真实经营现场的数据能力</h2>
          <p>依托在地协作、多源交叉验证和持续更新，沉淀公开渠道难以直接获得的成交、买家、物流与供需信息，形成可订阅的数据优势。</p>
        </div>
        <div className="potential-grid">
          {differentiated.map(([title,fields,method,product,value])=><article key={title}>
            <div><span>{value}</span><b>{title}</b></div>
            <p><strong>覆盖内容</strong>{fields}</p>
            <p><strong>获取与验证</strong>{method}</p>
            <p><strong>客户可获得</strong>{product}</p>
          </article>)}
        </div>
      </section>

      <section className="asset-pipeline" aria-label="数据产品形成流程"><span>多源采集</span><i>→</i><span>字段标准化</span><i>→</i><span>来源与置信等级</span><i>→</i><span>持续更新</span><i>→</i><strong>数据包 · 指数 · API · 订阅</strong></section>
    </main>
    <MarketingFooter/>
  </div>;
}
