"use client";
import { useEffect, useState, type ReactNode } from "react";

type Report={slug:string;title:string;type:string;country:string;summary:string;body:string;publishedAt:string|number|Date};
type ReportSource={evidenceId:string;title:string;url:string;publisher:string;publishedAt:string|number|Date;retrievedAt:string|number|Date};

function safeExternalUrl(value:string){
  try{const url=new URL(value);return (url.protocol==="http:"||url.protocol==="https:")&&!url.username&&!url.password?url.toString():null}catch{return null}
}

function InlineText({text}:{text:string}){
  const parts=text.split(/(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\)|\[S\d+\])/g).filter(Boolean);
  return <>{parts.map((part,i)=>{
    if(part.startsWith("**")&&part.endsWith("**"))return <strong key={i}>{part.slice(2,-2)}</strong>;
    if(part.startsWith("`")&&part.endsWith("`"))return <code key={i}>{part.slice(1,-1)}</code>;
    const link=part.match(/^\[([^\]]+)\]\(([^)]+)\)$/),url=link?safeExternalUrl(link[2]):null;
    if(link&&url)return <a key={i} href={url} target="_blank" rel="noopener noreferrer nofollow">{link[1]}</a>;
    const evidence=part.match(/^\[(S\d+)\]$/);
    if(evidence)return <sup key={i}>{evidence[1]}</sup>;
    return part as ReactNode;
  })}</>;
}

const cells=(line:string)=>line.trim().replace(/^\||\|$/g,"").split("|").map(cell=>cell.trim());
const isDivider=(line:string)=>cells(line).every(cell=>/^:?-{3,}:?$/.test(cell));

function ReportBody({body}:{body:string}){
  const lines=body.split(/\r?\n/),blocks:ReactNode[]=[];
  for(let i=0;i<lines.length;){
    const text=lines[i].trim();
    if(text.includes("|")&&i+1<lines.length&&isDivider(lines[i+1])){
      const header=cells(text),rows:string[][]=[];i+=2;
      while(i<lines.length&&lines[i].includes("|")&&lines[i].trim()){rows.push(cells(lines[i]));i++}
      blocks.push(<div className="report-table-wrap" key={`table-${i}`}><table className="report-table"><thead><tr>{header.map((cell,index)=><th scope="col" key={index}><InlineText text={cell}/></th>)}</tr></thead><tbody>{rows.map((row,rowIndex)=><tr key={rowIndex}>{header.map((_,cellIndex)=><td key={cellIndex}><InlineText text={row[cellIndex]??"—"}/></td>)}</tr>)}</tbody></table></div>);continue;
    }
    if(/^[-*+]\s+/.test(text)){
      const items:string[]=[];
      while(i<lines.length&&/^[-*+]\s+/.test(lines[i].trim())){items.push(lines[i].trim().replace(/^[-*+]\s+/,""));i++}
      blocks.push(<ul key={`list-${i}`}>{items.map((item,index)=><li key={index}><InlineText text={item}/></li>)}</ul>);continue;
    }
    if(!text){blocks.push(<span className="report-spacer" key={i}/>);i++;continue}
    if(text.startsWith("### "))blocks.push(<h3 key={i}><InlineText text={text.slice(4)}/></h3>);
    else if(text.startsWith("## "))blocks.push(<h2 key={i}><InlineText text={text.slice(3)}/></h2>);
    else if(text.startsWith("# "))blocks.push(<h2 key={i}><InlineText text={text.slice(2)}/></h2>);
    else if(text.startsWith("> "))blocks.push(<blockquote key={i}><InlineText text={text.slice(2)}/></blockquote>);
    else {const numbered=text.match(/^(\d+)\.\s+(.+)$/);blocks.push(numbered?<div className="report-numbered" key={i}><b>{numbered[1].padStart(2,"0")}</b><p><InlineText text={numbered[2]}/></p></div>:<p key={i}><InlineText text={text}/></p>)}
    i++;
  }
  return <div className="report-body">{blocks}</div>;
}

export default function ReportDetailClient({slug}:{slug:string}){
  const [report,setReport]=useState<Report|null>(null),[sources,setSources]=useState<ReportSource[]>([]),[error,setError]=useState("");
  useEffect(()=>{
    const controller=new AbortController();
    fetch(`/api/ingest/report?slug=${encodeURIComponent(slug)}`,{signal:controller.signal}).then(async response=>{
      const payload=await response.json() as {records?:Report[];sources?:ReportSource[]};
      if(!response.ok||!payload.records?.[0])throw new Error("未找到这份报告");
      setReport(payload.records[0]);setSources(payload.sources??[]);
    }).catch(reason=>{if(reason instanceof Error&&reason.name!=="AbortError")setError(reason.message)});
    return ()=>controller.abort();
  },[slug]);
  if(error)return <section className="report-state"><b>{error}</b>{/* Native navigation avoids the current vinext client-router failure. */}<a href="/reports" data-native-navigation="true">返回报告中心 →</a></section>;
  if(!report)return <section className="report-state" aria-live="polite">正在读取报告…</section>;
  const date=new Date(report.publishedAt).toLocaleDateString("zh-CN");
  return <>{/* Native navigation avoids the current vinext client-router failure. */}<a className="report-back" href="/reports" data-native-navigation="true">← 返回报告中心</a><article className="report-detail"><header><div className="tag-row"><b>{report.type}</b><b>中亚五国</b></div><h1>{report.title}</h1><p>{report.summary}</p><small>{date} · 数据来源：因恒科技</small></header><ReportBody body={report.body}/>{sources.length>0&&<section className="report-evidence"><h2>可核验资料</h2>{sources.map(source=><a href={safeExternalUrl(source.url)??"#"} target="_blank" rel="noopener noreferrer nofollow" key={source.evidenceId}><b>{source.evidenceId}</b><span>{source.publisher}：{source.title}</span><small>{new Date(source.publishedAt).toLocaleDateString("zh-CN")} 发布 · {new Date(source.retrievedAt).toLocaleDateString("zh-CN")} 检索</small></a>)}</section>}</article></>;
}
