import SiteNav from "../site-nav";
import MarketingFooter from "../marketing-footer";

const available = [
  ["官方贸易", "UN Comtrade、中国出口镜像", "国家/伙伴/流向/HS/金额/数量/年份", "市场规模、增长趋势、镜像核验"],
  ["农业供给", "FAOSTAT、中国供给资源", "国家/品类/产量/年份/估算标识", "供需粗估、品类筛选"],
  ["市场价格", "电商、商超、批发挂牌", "城市/渠道/产品/规格/币种/日期/来源", "价格带、渠道地图、周报"],
  ["市场信号", "行业媒体、访谈与公开资料", "事件/主体/市场/日期/证据等级", "市场摘要、机会提示"],
];
const potential = [
  ["真实成交数据库", "成交价、采购量、规格、账期、频次", "合作商回传 + 定向调研", "价格指数、采购基准", "高"],
  ["进口商与买家图谱", "企业、联系人、品类、采购周期、信用", "工商数据 + 展会 + 渠道验证", "买家库、销售线索订阅", "高"],
  ["喀什—中亚物流指数", "线路、报价、时效、冷链损耗、通关异常", "货代/口岸/承运商周度采集", "物流成本指数、线路API", "高"],
  ["项目与投资数据库", "园区、项目、产能、资金需求、进度、合作方", "政府公开信息 + 在地跟踪", "项目库、投资机会订阅", "中高"],
  ["政策与合规知识库", "关税、检疫、准入、补贴、政策变化", "法规监测 + 专家复核", "合规提醒、品类准入包", "中高"],
  ["农业供需预测集", "月度消费、库存、产地、天气、季节性", "多源建模 + 持续校准", "预测模型、行业指数", "中"],
];

export default function AssetsPage(){return <div className="marketing-site"><SiteNav/><main className="subpage"><section className="subhero"><span>DATA ASSETS</span><h1>把零散信息，沉淀为可销售的数据资产</h1><p>现有数据先形成可信基线；缺失但具商业价值的数据进入采集路线图，明确字段、来源、产品形态和优先级。</p></section><section className="asset-section"><div className="landing-heading"><span>AVAILABLE NOW</span><h2>现有可用数据</h2></div><div className="data-table"><div className="data-table-head"><span>数据域</span><span>来源</span><span>核心字段</span><span>当前用途</span></div>{available.map(row=><div className="data-table-row" key={row[0]}>{row.map((cell,i)=><span key={cell} className={i===0?"cell-title":""}>{cell}</span>)}</div>)}</div></section><section className="asset-section asset-future-section"><div className="landing-heading"><span>COMMERCIAL ROADMAP</span><h2>现在没有，但确有商业价值的数据</h2><p>优先建设难以从公开渠道直接获得、能形成持续订阅和交易价值的数据。</p></div><div className="potential-grid">{potential.map(([title,fields,method,product,priority])=><article key={title}><div><span>{priority}优先级</span><b>{title}</b></div><p><strong>关键字段</strong>{fields}</p><p><strong>采集方式</strong>{method}</p><p><strong>可售产品</strong>{product}</p></article>)}</div></section><section className="asset-pipeline"><span>原始信息</span><i>→</i><span>字段标准化</span><i>→</i><span>来源与置信等级</span><i>→</i><span>持续更新</span><i>→</i><strong>数据包 · 指数 · API · 订阅</strong></section></main><MarketingFooter/></div>}
