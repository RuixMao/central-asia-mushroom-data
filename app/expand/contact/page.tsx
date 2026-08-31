"use client";
import { FormEvent, useState } from "react";
import ProductShell from "../../product-shell";
import { targetMarkets } from "../../market-scope";

const markets = [...targetMarkets.map((market) => market.name), "尚未确定"];

export default function Page() {
  const [draft, setDraft] = useState("");
  const [copied, setCopied] = useState(false);
  function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const data = new FormData(e.currentTarget);
    setDraft(["食用菌出海市场验证需求", `联系人：${data.get("name")}`, `企业：${data.get("company")}`, `联系方式：${data.get("contact")}`, `产品：${data.get("product")}`, `产能/供应能力：${data.get("capacity")}`, `目标国家：${data.get("country")}`, `合作需求：${data.get("need")}`].join("\n"));
    setCopied(false);
  }
  async function copy() { await navigator.clipboard.writeText(draft); setCopied(true); }
  return <ProductShell><main className="saas-main"><section className="saas-hero compact"><span>MARKET VALIDATION</span><h1>提交目标市场验证需求</h1><p>填写产品、产能、目标国家和合作需求，生成市场验证清单。</p></section>{draft ? <section className="contact-draft"><span>市场验证需求清单</span><h2>复制清单，发给您的商务对接人</h2><pre>{draft}</pre><div><button type="button" onClick={copy}>{copied ? "已复制" : "复制需求内容"}</button><button type="button" onClick={() => setDraft("")}>返回修改</button></div></section> : <form className="expand-form" onSubmit={submit}><label>联系人<input name="name" required /></label><label>企业<input name="company" required /></label><label>联系方式<input name="contact" required placeholder="手机、微信或邮箱" /></label><label>目标国家<select name="country" required>{markets.map(market => <option key={market}>{market}</option>)}</select></label><label>产品<input name="product" required placeholder="品类、形态与规格" /></label><label>产能或供应能力<input name="capacity" required placeholder="例如：月供 20 吨；冷链可发货" /></label><label className="full">合作需求<textarea name="need" required placeholder="请说明希望验证的价格、渠道、物流、准入或合作问题" /></label><button type="submit">生成市场验证需求清单 →</button></form>}</main></ProductShell>;
}
