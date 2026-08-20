"""把已生成日报写入微信公众号草稿箱；只建草稿，不调用发表接口。"""

import html
import json
import os
import re
import sys
from pathlib import Path

import markdown
import requests
from bs4 import BeautifulSoup

API_BASE = "https://api.weixin.qq.com"


class WeChatError(RuntimeError):
    pass


def require_env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise WeChatError(f"缺少加密环境变量 {name}")
    return value


def api_json(method, path, *, token=None, **kwargs):
    url = f"{API_BASE}{path}"
    if token:
        kwargs.setdefault("params", {})["access_token"] = token
    response = requests.request(method, url, timeout=60, **kwargs)
    response.raise_for_status()
    result = response.json()
    if result.get("errcode", 0):
        raise WeChatError(f"微信接口失败 errcode={result.get('errcode')} errmsg={result.get('errmsg')}")
    return result


def get_access_token(app_id, app_secret):
    result = api_json("POST", "/cgi-bin/stable_token", json={
        "grant_type": "client_credential",
        "appid": app_id,
        "secret": app_secret,
        "force_refresh": False,
    })
    token = result.get("access_token")
    if not token:
        raise WeChatError("微信未返回 access_token")
    return token


def markdown_to_wechat_html(text):
    rendered = markdown.markdown(text, extensions=["tables", "sane_lists"])
    soup = BeautifulSoup(rendered, "html.parser")
    styles = {
        "h2": "margin:28px 0 12px;font-size:20px;line-height:1.5;color:#173d32;font-weight:700;border-left:4px solid #2f7d64;padding-left:10px;",
        "h3": "margin:22px 0 10px;font-size:17px;line-height:1.5;color:#173d32;font-weight:700;",
        "p": "margin:10px 0;font-size:15px;line-height:1.85;color:#26352f;letter-spacing:.2px;",
        "ul": "margin:10px 0;padding-left:22px;color:#26352f;",
        "ol": "margin:10px 0;padding-left:22px;color:#26352f;",
        "li": "margin:7px 0;font-size:15px;line-height:1.75;color:#26352f;",
        "strong": "font-weight:700;color:#163f33;",
        "blockquote": "margin:16px 0;padding:12px 14px;background:#f3f7f5;border-left:3px solid #70a995;color:#496159;",
        "table": "width:100%;border-collapse:collapse;margin:14px 0;font-size:13px;line-height:1.55;",
        "th": "border:1px solid #d9e3df;padding:7px 5px;background:#eef5f2;color:#173d32;font-weight:700;",
        "td": "border:1px solid #d9e3df;padding:7px 5px;color:#31433d;vertical-align:top;",
    }
    for tag_name, style in styles.items():
        for tag in soup.find_all(tag_name):
            tag["style"] = style
    for tag in soup.find_all(["script", "style"]):
        tag.decompose()
    return f'<section style="font-family:-apple-system,BlinkMacSystemFont,\'PingFang SC\',\'Microsoft YaHei\',sans-serif;padding:0 4px;">{soup}</section>'


def recent_draft_titles(token):
    result = api_json("POST", "/cgi-bin/draft/batchget", token=token, json={"offset": 0, "count": 20, "no_content": 1})
    titles = set()
    for item in result.get("item", []):
        content = item.get("content", {})
        for article in content.get("news_item", []):
            if article.get("title"):
                titles.add(article["title"].strip())
    return titles


def upload_cover(token, cover_path):
    with cover_path.open("rb") as image_file:
        result = api_json("POST", "/cgi-bin/material/add_material", token=token,
                          params={"type": "image"}, files={"media": (cover_path.name, image_file, "image/png")})
    media_id = result.get("media_id")
    if not media_id:
        raise WeChatError("微信未返回封面 media_id")
    return media_id


def add_draft(token, artifact, thumb_media_id):
    source_url = ""
    slug = artifact.get("slug")
    if slug:
        source_url = f"https://data.yinheng.site/reports/{slug}"
    payload = {"articles": [{
        "article_type": "news",
        "title": artifact["title"][:64],
        "author": os.environ.get("WECHAT_AUTHOR", "因恒科技")[:16],
        "digest": re.sub(r"[#*_>`]", "", artifact.get("summary", ""))[:120],
        "content": markdown_to_wechat_html(artifact["body"]),
        "content_source_url": source_url,
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }]}
    return api_json("POST", "/cgi-bin/draft/add", token=token, json=payload)


def run():
    artifact_path = Path(os.environ.get("REPORT_ARTIFACT_OUTPUT", "tmp/daily-report.json"))
    cover_path = Path(os.environ.get("WECHAT_COVER_PATH", "public/og.png"))
    if not cover_path.is_file():
        raise WeChatError(f"公众号封面不存在：{cover_path}")
    if artifact_path.is_file():
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    else:
        # 仅供人工触发的连通性测试使用；正式日报始终读取本轮生成产物。
        site_url = os.environ.get("SITE_URL", "").rstrip("/")
        if not site_url:
            raise WeChatError(f"日报产物不存在：{artifact_path}")
        response = requests.get(f"{site_url}/api/ingest/report", timeout=60)
        response.raise_for_status()
        reports = [row for row in response.json().get("records", []) if row.get("type") == "daily"]
        if not reports:
            raise WeChatError("线上没有可用于测试的日报")
        latest = reports[0]
        artifact = {key: latest.get(key, "") for key in ("title", "summary", "body", "slug")}
    token = get_access_token(require_env("WECHAT_APP_ID"), require_env("WECHAT_APP_SECRET"))
    title = artifact["title"][:64]
    if title in recent_draft_titles(token):
        print(f"公众号草稿已存在，跳过重复创建：{title}")
        return
    thumb_media_id = os.environ.get("WECHAT_COVER_MEDIA_ID", "").strip() or upload_cover(token, cover_path)
    result = add_draft(token, artifact, thumb_media_id)
    print(f"公众号草稿创建成功：{title}，media_id={result.get('media_id', '')}")


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        print(f"公众号草稿创建失败：{exc}", file=sys.stderr)
        raise
