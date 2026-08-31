export type CaseStudy={title:string;market:string;date:string;facts:string[];source:string;url:string};
export type CaseTopic={slug:string;label:string;title:string;intro:string;cases:CaseStudy[]};

export const caseTopics:CaseTopic[]=[
  {slug:"export",label:"出口与海外客户",title:"食用菌出口与海外客户案例",intro:"展示公开材料中的出口市场、产品、数量与海外客户拓展。",cases:[
    {title:"灌南县食用菌企业拓展菲律宾等海外市场",market:"菲律宾、韩国、北美等",date:"2025",facts:["企业出口创汇超过390万美元","丽莎菌业在美国、加拿大建设的菌菇工厂已生产","企业与土耳其客户洽谈项目合作及菌包销售"],source:"灌南县人民政府《菌菇产业》",url:"https://www.guannan.gov.cn/gnzx/upload/ce219fde-3bc2-4203-a6a8-8677a5534a90.pdf"},
    {title:"连云港企业食用菌出口东南亚",market:"东南亚、日本、美国",date:"2017",facts:["公开报道企业出口超过300吨","出口金额超过300万元","产品包括香菇、木耳等"],source:"中国供销合作网",url:"https://www.chinacoop.gov.cn/HTML/2017/10/12/124728.html"},
  ]},
  {slug:"overseas-project",label:"海外项目与示范",title:"海外食用菌合作与示范项目",intro:"展示海外技术合作、示范基地和项目落地材料。",cases:[
    {title:"中泰农业食品研发中心开展平菇示范项目",market:"泰国信武里",date:"2020",facts:["首期项目为平菇夏季高产栽培技术示范推广","项目周期三年","指导当地农业技术学院升级设施并建设区域示范基地"],source:"北京市教育委员会公开报告",url:"https://jw.beijing.gov.cn/bjzj/gdzyreport/gdreport/202003/P020260303377936610902.pdf"},
    {title:"塔吉克斯坦—中国农业合作示范园",market:"塔吉克斯坦",date:"2022",facts:["列入首批境外农业合作示范区建设试点","用于农业企业抱团出海与产业集聚","可作为食用菌设施农业项目的园区条件参考"],source:"上海市商务委员会研究报告",url:"https://segg.sh.gov.cn/zxfw/yjbg/zhbg/index/7b8e529d05f24087b2bccaf2169aa2b5.pdf"},
  ]},
  {slug:"spawn",label:"菌包与产能输出",title:"菌包、设备与产能输出案例",intro:"展示菌包出口、产能合作与工厂化生产能力。",cases:[
    {title:"灌南企业向海外销售菌包并洽谈项目合作",market:"土耳其及其他海外市场",date:"2025",facts:["公开材料记录对外销售香姬菇菌包","企业与土耳其方面洽谈项目合作","海外客户拓展与工厂落地同步推进"],source:"灌南县人民政府《菌菇产业》",url:"https://www.guannan.gov.cn/gnzx/upload/ce219fde-3bc2-4203-a6a8-8677a5534a90.pdf"},
    {title:"土库曼斯坦 Tiz hyzmat 双孢菇生产项目",market:"土库曼斯坦",date:"2022",facts:["政府官网披露当地双孢菇生产企业","现有产出约6吨/月","规划产能600吨/年，远期2500吨/年"],source:"土库曼斯坦政府",url:"https://turkmenistan.gov.tm/ru/post/65371/shampinony-ot-tiz-hyzmat"},
  ]},
  {slug:"smart-farm",label:"智慧设施与方舱",title:"智慧设施与工厂化生产案例",intro:"展示智能环境控制、方舱和标准化生产项目。",cases:[
    {title:"昌宁县食药用菌产业园智能化方舱规划",market:"面向南亚、东南亚市场",date:"2025-08-08",facts:["项目规划智能化方舱与标准化种植示范区","配置冷链物流、精深加工与营销体系","项目投资初步估算10亿元"],source:"昌宁县人民政府",url:"https://www.yncn.gov.cn/info/1025/9230680.htm"},
  ]},
];

export const getCaseTopic=(slug:string)=>caseTopics.find(topic=>topic.slug===slug);
