import SiteNav from "../site-nav";
import MarketingFooter from "../marketing-footer";

const capabilities=[
  {status:"已上线",title:"官方贸易与市场规模",scope:"中亚五国；HS 070951、070959、200310",source:"UN Comtrade 与伙伴国镜像",cadence:"年度基线，接口按来源更新",delivery:"国别规模、品类结构、来源口径与证据等级"},
  {status:"已上线",title:"五国公开价格监测",scope:"五国主要城市、已接入零售与电商渠道",source:"公开商品页与平台搜索页",cadence:"每日采集",delivery:"SKU 明细、原币价格、USD/kg、规格和来源页"},
  {status:"已上线",title:"市场报告与商机信号",scope:"五国食用菌价格、贸易与已核验证据",source:"平台数据、公开资料与报告证据包",cadence:"日报及专题更新",delivery:"结论、证据、风险与下一步验证任务"},
  {status:"验证中",title:"国别市场进入研究",scope:"优先覆盖哈萨克斯坦与乌兹别克斯坦",source:"贸易、价格、渠道观察与公开准入资料",cadence:"随证据更新",delivery:"市场判断、证据缺口、风险清单与验证建议"},
  {status:"共建中",title:"真实成交与采购基准",scope:"具体品类、规格、账期与采购频次",source:"合作方回传与定向调研",cadence:"按合作项目持续沉淀",delivery:"成交区间、采购基准与渠道验证记录"},
  {status:"共建中",title:"买家、物流与准入验证",scope:"买家周期、线路时效、冷链损耗与准入要求",source:"在地伙伴、货代、口岸与专家复核",cadence:"按项目和线路更新",delivery:"验证清单、到岸成本模型与合作推进建议"},
];

export default function AssetsPage(){return <div className="marketing-site"><SiteNav/><main className="subpage data-assets-page">
  <section className="subhero"><span>PLATFORM CAPABILITIES</span><h1>从公开证据到市场进入验证</h1><p>每项能力均明确覆盖内容、来源、频率、交付成果和当前状态；规划中的能力不会包装成成熟产品。</p></section>
  <section className="asset-section"><div className="landing-heading"><span>CAPABILITY STATUS</span><h2>平台能力清单</h2><p>“已上线”可直接查看；“验证中”已有数据基础，仍在完善实测；“共建中”需要真实业务与合作伙伴持续沉淀。</p></div><div className="capability-status-grid">{capabilities.map(item=><article key={item.title}><header><span className={`capability-status status-${item.status}`}>{item.status}</span><h2>{item.title}</h2></header><dl><div><dt>覆盖内容</dt><dd>{item.scope}</dd></div><div><dt>数据来源</dt><dd>{item.source}</dd></div><div><dt>更新频率</dt><dd>{item.cadence}</dd></div><div><dt>客户可获得</dt><dd>{item.delivery}</dd></div></dl></article>)}</div></section>
  <section className="asset-pipeline" aria-label="数据形成流程"><span>多源采集</span><i>→</i><span>字段标准化</span><i>→</i><span>来源与置信等级</span><i>→</i><span>持续验证</span><i>→</i><strong>市场判断 · 验证清单 · 持续监测</strong></section>
</main><MarketingFooter/></div>}
